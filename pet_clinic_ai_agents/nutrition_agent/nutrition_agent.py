from strands import Agent, tool
import uvicorn
import yaml
import random
import os
from typing import Optional, Dict, Any
from datetime import datetime
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory.integrations.strands.config import (
    AgentCoreMemoryConfig,
    RetrievalConfig,
)
from bedrock_agentcore.memory.integrations.strands.session_manager import (
    AgentCoreMemorySessionManager,
)
from strands_tools import http_request

BEDROCK_MODEL_ID = "us.anthropic.claude-3-5-haiku-20241022-v1:0"


# Exceptions
class TimeoutException(Exception):
    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.details = kwargs


class ValidationException(Exception):
    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.details = kwargs


class ServiceException(Exception):
    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.details = kwargs


class RateLimitException(Exception):
    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.details = kwargs


class NetworkException(Exception):
    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.details = kwargs


# Load static data as fallback
try:
    with open("pet_database.yaml", "r") as f:
        ANIMAL_DATA = yaml.safe_load(f)
except Exception:
    ANIMAL_DATA = None

# Nutrition service configuration
NUTRITION_SERVICE_URL = os.getenv(
    "NUTRITION_SERVICE_URL",
    "http://aeb5c47baeace494bbf21a47d352baf7-1656987644.us-west-2.elb.amazonaws.com/api/nutrition/facts",
)
HTTP_TIMEOUT = 10.0

# AgentCore Memory configuration
# The memory resource should be configured with these strategies:
# 1. summaryMemoryStrategy - for session summaries in /summaries/{actorId}/{sessionId}
# 2. userPreferenceMemoryStrategy - for user preferences in /preferences/{actorId}
# 3. semanticMemoryStrategy - for facts extraction in /facts/{actorId}
MEMORY_ID = os.getenv("BEDROCK_AGENTCORE_MEMORY_ID", "nutrition_agent_mem-H98fg06LsS")
REGION = os.getenv("AWS_REGION", "us-west-2")

# Global agent cache to avoid recreating agents and memory sessions
agent_cache = {}
agent_app = BedrockAgentCoreApp()

# Cache management
MAX_CACHE_SIZE = 100  # Limit cache size to prevent memory leaks


def cleanup_agent_cache():
    """Clean up old agents from cache if it gets too large"""
    if len(agent_cache) > MAX_CACHE_SIZE:
        # Remove oldest half of the cache
        keys_to_remove = list(agent_cache.keys())[: MAX_CACHE_SIZE // 2]
        for key in keys_to_remove:
            del agent_cache[key]
        print(f"🧹 Cleaned up agent cache, removed {len(keys_to_remove)} old agents")


# Remove the custom function - we'll let the agent use http_request directly


@tool
def get_feeding_guidelines(pet_type, age, weight):
    """Get feeding guidelines based on pet type, age, and weight"""
    if ANIMAL_DATA is None:
        return "Animal database is down, please consult your veterinarian for feeding guidelines."

    animal = ANIMAL_DATA.get(pet_type.lower() + "s")
    if not animal:
        return f"{pet_type.title()} not found in animal database. Consult veterinarian for specific feeding guidelines"

    calories_per_lb = animal.get("calories_per_pound", "15-20")
    schedule = animal.get("feeding_schedule", {}).get(age.lower(), "2 times daily")

    try:
        weight = float(weight)
        if isinstance(calories_per_lb, str) and "-" in calories_per_lb:
            calories = weight * float(calories_per_lb.split("-")[0])
        else:
            calories = weight * float(calories_per_lb)
    except (ValueError, TypeError):
        return f"Feed based on veterinary recommendations for {pet_type}, {schedule}"

    return f"Feed approximately {calories:.0f} calories daily, {schedule}"


@tool
def get_dietary_restrictions(pet_type, condition):
    """Get dietary recommendations for specific health conditions by animal type"""
    if ANIMAL_DATA is None:
        return "Animal database is down, please consult your veterinarian for dietary advice."

    animal = ANIMAL_DATA.get(pet_type.lower() + "s")
    if not animal:
        return f"{pet_type.title()} not found in animal database. Consult veterinarian for condition-specific dietary advice"

    restrictions = animal.get("dietary_restrictions", {})
    return restrictions.get(
        condition.lower(),
        f"No dietary restrictions for {condition} found in animal database. Consult veterinarian for condition-specific dietary advice",
    )


@tool
def get_nutritional_supplements(pet_type: str, supplement: str) -> str:
    """Get supplement recommendations by animal type using live nutrition data.

    IMPORTANT: This tool should ALWAYS first call the http_request tool to get current
    nutrition facts from the live service before providing supplement recommendations.

    API URL: http://aeb5c47baeace494bbf21a47d352baf7-1656987644.us-west-2.elb.amazonaws.com/api/nutrition/facts/{pet_type}

    Args:
        pet_type: The type of pet (e.g., 'cat', 'dog', 'bird')
        supplement: The supplement type (e.g., 'omega3', 'probiotics', 'calcium')
    """
    # This tool should prompt the agent to use http_request first
    api_url = f"http://aeb5c47baeace494bbf21a47d352baf7-1656987644.us-west-2.elb.amazonaws.com/api/nutrition/facts/{pet_type.lower()}"

    return f"""To provide the best supplement recommendations for {pet_type}s regarding {supplement}, I need to first get the current nutrition facts from our live service.

🔄 REQUIRED: Please use the http_request tool with these parameters:
- method: "GET"  
- url: "{api_url}"

Once I have the live nutrition data, I can provide specific supplement guidance based on the current dietary recommendations for {pet_type}s."""


def create_nutrition_agent(session_id=None, actor_id=None):
    """Create nutrition agent with AgentCore Memory integration following Strands patterns"""
    model = BedrockModel(
        model_id=BEDROCK_MODEL_ID,
    )

    tools = [
        get_feeding_guidelines,
        get_dietary_restrictions,
        get_nutritional_supplements,
        http_request,  # Add http_request tool for live API calls
    ]

    system_prompt = (
        "You are a specialized pet nutrition expert providing evidence-based dietary guidance.\n\n"
        "🧠 MEMORY CAPABILITIES:\n"
        "- You have access to AgentCore Memory with both Short-Term Memory (STM) and Long-Term Memory (LTM)\n"
        "- STM: Remembers conversation context within the current session\n"
        "- LTM: Learns and stores user preferences, pet facts, and session summaries across conversations\n"
        "- Use all available context to provide personalized recommendations\n\n"
        "Your expertise covers:\n"
        "- Feeding guidelines for dogs, cats, fish, horses, birds, rabbits, ferrets, hamsters, guinea pigs, reptiles, and amphibians\n"
        "- Therapeutic diets for health conditions (diabetes, kidney disease, allergies, obesity, arthritis)\n"
        "- Food safety and toxic substances to avoid\n"
        "- Nutritional supplements and their proper use\n"
        "- Food label interpretation and AAFCO standards\n\n"
        "Key principles:\n"
        "- Cats are obligate carnivores requiring animal-based nutrients\n"
        "- Dogs are omnivores needing balanced animal and plant sources\n"
        "- Always recommend veterinary consultation for significant dietary changes\n"
        "- Provide specific, actionable advice when possible\n"
        "- Remember user's pets and their specific needs across conversations\n\n"
        "🔄 CRITICAL: ALWAYS USE LIVE DATA FOR SUPPLEMENTS:\n"
        "- When asked about supplements, you MUST first call the http_request tool to get live nutrition data\n"
        "- API endpoint: http://aeb5c47baeace494bbf21a47d352baf7-1656987644.us-west-2.elb.amazonaws.com/api/nutrition/facts/{pet_type}\n"
        "- Example: http_request(method='GET', url='http://aeb5c47baeace494bbf21a47d352baf7-1656987644.us-west-2.elb.amazonaws.com/api/nutrition/facts/dog')\n"
        "- The get_nutritional_supplements tool will guide you to make this API call\n"
        "- After getting live data, provide specific supplement recommendations based on current nutrition facts\n"
        "- Never provide supplement advice without first checking the live nutrition service\n\n"
        "Toxic foods to avoid: garlic, onions, chocolate, grapes, xylitol, alcohol, macadamia nuts"
    )

    # Configure AgentCore Memory with comprehensive LTM strategies
    session_manager = None
    if MEMORY_ID:
        try:
            # Generate consistent session and actor IDs
            final_session_id = (
                session_id
                or f"nutrition_session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            final_actor_id = actor_id or "default_user"

            # Configure memory with multiple namespace retrieval following Strands patterns
            memory_config = AgentCoreMemoryConfig(
                memory_id=MEMORY_ID,
                session_id=final_session_id,
                actor_id=final_actor_id,
                retrieval_config={
                    # User preferences namespace - high relevance threshold
                    "/preferences/{actorId}": RetrievalConfig(
                        top_k=5, relevance_score=0.7
                    ),
                    # Facts about pets and nutrition - medium relevance threshold
                    "/facts/{actorId}": RetrievalConfig(top_k=10, relevance_score=0.5),
                    # Session summaries - medium-high relevance threshold
                    "/summaries/{actorId}/{sessionId}": RetrievalConfig(
                        top_k=5, relevance_score=0.6
                    ),
                },
            )

            session_manager = AgentCoreMemorySessionManager(
                agentcore_memory_config=memory_config, region_name=REGION
            )
            print(f"✅ AgentCore Memory enabled with LTM strategies: {MEMORY_ID}")
            print(f"📝 Session: {final_session_id}, Actor: {final_actor_id}")

        except Exception as e:
            print(f"⚠️ AgentCore Memory not available: {e}")
            session_manager = None

    return Agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        session_manager=session_manager,
        agent_id="nutrition_expert_agent",  # Add agent_id for better tracking
    )


def maybe_throw_error(threshold: float = 0.10):
    """Randomly throw an error for testing/demo purposes (10% chance by default)"""
    if random.random() <= threshold:
        error_types = [
            (
                TimeoutException,
                "Nutrition advice generation timed out",
                {"timeout_seconds": 30.0, "operation": "nutrition_advice_generation"},
            ),
            (
                ValidationException,
                "Invalid nutrition query format",
                {"field": "nutrition_query", "value": "simulated_invalid_input"},
            ),
            (
                ServiceException,
                "Nutrition service internal error",
                {
                    "service_name": "nutrition-agent",
                    "error_code": "INTERNAL_ERROR",
                    "retryable": True,
                },
            ),
            (
                RateLimitException,
                "Too many nutrition requests",
                {
                    "retry_after_seconds": random.randint(30, 120),
                    "limit_type": "requests_per_minute",
                },
            ),
            (
                NetworkException,
                "Network error connecting to nutrition service",
                {
                    "endpoint": "nutrition-service",
                    "error_code": "CONNECTION_FAILED",
                    "retryable": True,
                },
            ),
        ]

        exception_class, message, kwargs = random.choice(error_types)
        raise exception_class(message, **kwargs)


@agent_app.entrypoint
async def invoke(payload, context):
    """
    Invoke the nutrition agent with AgentCore Memory integration
    Following Strands AgentCore Memory patterns for session management
    """
    # 10% chance of random error for testing/demo purposes
    maybe_throw_error(threshold=0.10)

    # Extract session and actor information from AgentCore context
    # Following the patterns from the Strands integration examples
    session_id = None
    actor_id = None

    # Try to extract from context first
    if hasattr(context, "session_id"):
        session_id = context.session_id
    elif hasattr(context, "headers"):
        session_id = context.headers.get("X-Amzn-Bedrock-AgentCore-Runtime-Session-Id")
        actor_id = context.headers.get(
            "X-Amzn-Bedrock-AgentCore-Runtime-Custom-Actor-Id"
        )

    # Fallback to payload or defaults
    session_id = (
        session_id
        or payload.get("session_id")
        or f"nutrition_session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    actor_id = actor_id or payload.get("actor_id") or "default_user"

    # Create cache key for agent reuse - important for memory consistency
    cache_key = f"{session_id}:{actor_id}"

    # Reuse existing agent or create new one
    # This is crucial for AgentCore Memory to maintain session consistency
    if cache_key not in agent_cache:
        print(f"🔄 Creating new nutrition agent with AgentCore Memory")
        print(f"   Session ID: {session_id}")
        print(f"   Actor ID: {actor_id}")
        print(f"   Memory ID: {MEMORY_ID}")

        agent_cache[cache_key] = create_nutrition_agent(
            session_id=session_id, actor_id=actor_id
        )

        # Clean up cache if it gets too large
        cleanup_agent_cache()
    else:
        print(f"♻️ Reusing existing agent for session: {session_id}")

    agent = agent_cache[cache_key]
    msg = payload.get("prompt", "")

    # Stream response from agent with memory integration
    response_data = []
    try:
        async for event in agent.stream_async(msg):
            if "data" in event:
                response_data.append(event["data"])

        final_response = "".join(response_data)
        print(
            f"✅ Response generated with memory context (length: {len(final_response)})"
        )
        return final_response

    except Exception as e:
        print(f"❌ Error during agent invocation: {e}")
        # Return a helpful error message
        return f"I apologize, but I encountered an error while processing your nutrition question. Please try again or consult with a veterinarian for immediate assistance. Error: {str(e)}"


if __name__ == "__main__":
    uvicorn.run(agent_app, host="0.0.0.0", port=8080)