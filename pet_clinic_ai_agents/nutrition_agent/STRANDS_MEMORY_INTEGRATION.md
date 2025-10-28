# Strands AgentCore Memory Integration

This nutrition agent has been enhanced with **Strands AgentCore Memory integration**, providing both Short-Term Memory (STM) and Long-Term Memory (LTM) capabilities for persistent, personalized conversations.

## 🧠 Memory Capabilities

### Short-Term Memory (STM)
- **Purpose**: Maintains conversation context within a single session
- **Storage**: Conversation messages and immediate context
- **Scope**: Current session only

### Long-Term Memory (LTM)
- **Purpose**: Learns and stores information across multiple sessions
- **Strategies**: 
  - `userPreferenceMemoryStrategy`: User food preferences, pet care preferences
  - `semanticMemoryStrategy`: Facts about pets, health conditions, dietary needs
  - `summaryMemoryStrategy`: Session summaries for context continuity

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Nutrition Agent                         │
├─────────────────────────────────────────────────────────────┤
│  • Strands Agent with BedrockModel                         │
│  • Tools: feeding_guidelines, supplements, http_request     │
│  • AgentCoreMemorySessionManager                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              AgentCore Memory Service                       │
├─────────────────────────────────────────────────────────────┤
│  Namespaces:                                               │
│  • /preferences/{actorId}     - User preferences           │
│  • /facts/{actorId}          - Pet & nutrition facts       │
│  • /summaries/{actorId}/{sessionId} - Session summaries    │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Setup Instructions

### 1. Prerequisites

```bash
pip install 'bedrock-agentcore[strands-agents]'
```

### 2. Environment Variables

```bash
export BEDROCK_AGENTCORE_MEMORY_ID="your-memory-resource-id"
export AWS_REGION="us-west-2"
```

### 3. AgentCore Memory Resource Configuration

Your AgentCore Memory resource must be configured with these strategies:

```python
# Example memory creation with required strategies
memory = client.create_memory_and_wait(
    name="NutritionAgentMemory",
    description="Memory for pet nutrition agent with LTM capabilities",
    strategies=[
        {
            "summaryMemoryStrategy": {
                "name": "SessionSummarizer",
                "namespaces": ["/summaries/{actorId}/{sessionId}"]
            }
        },
        {
            "userPreferenceMemoryStrategy": {
                "name": "PreferenceLearner", 
                "namespaces": ["/preferences/{actorId}"]
            }
        },
        {
            "semanticMemoryStrategy": {
                "name": "FactExtractor",
                "namespaces": ["/facts/{actorId}"]
            }
        }
    ]
)
```

## 🔧 Configuration Details

### Memory Configuration

```python
memory_config = AgentCoreMemoryConfig(
    memory_id=MEMORY_ID,
    session_id=session_id,
    actor_id=actor_id,
    retrieval_config={
        # High relevance for user preferences
        "/preferences/{actorId}": RetrievalConfig(
            top_k=5,
            relevance_score=0.7
        ),
        # Medium relevance for facts
        "/facts/{actorId}": RetrievalConfig(
            top_k=10,
            relevance_score=0.5
        ),
        # Medium-high relevance for summaries
        "/summaries/{actorId}/{sessionId}": RetrievalConfig(
            top_k=5,
            relevance_score=0.6
        ),
    },
)
```

### Retrieval Configuration Parameters

- **`top_k`**: Number of most relevant memories to retrieve (1-1000)
- **`relevance_score`**: Minimum similarity threshold (0.0-1.0)
- **`strategy_id`**: Optional filter for specific memory strategies

## 📝 Usage Examples

### Basic Usage

```python
from nutrition_agent import create_nutrition_agent

# Create agent with memory
agent = create_nutrition_agent(
    session_id="user_session_123",
    actor_id="user_456"
)

# First conversation - establishes preferences
response1 = await agent.async_invoke(
    "I have a Golden Retriever named Max, 65 lbs, very active. "
    "I prefer grain-free, natural foods."
)

# Later conversation - agent remembers Max and preferences
response2 = await agent.async_invoke(
    "What supplements would be good for Max?"
)
```

### Cross-Session Memory

```python
# Session 1
agent1 = create_nutrition_agent(
    session_id="session_1", 
    actor_id="user_123"
)
await agent1.async_invoke("My cat Whiskers has kidney disease...")

# Session 2 (different session, same user)
agent2 = create_nutrition_agent(
    session_id="session_2", 
    actor_id="user_123"  # Same actor
)
# Agent remembers Whiskers and kidney disease from LTM
await agent2.async_invoke("What's the best food for Whiskers now?")
```

## 🧪 Testing

Run the test script to verify memory integration:

```bash
python test_strands_memory.py
```

This will test:
- ✅ Memory persistence within a session
- ✅ Cross-session memory retrieval
- ✅ Live API integration for supplements
- ✅ Personalized recommendations based on stored preferences

## 🔍 Memory Namespaces

### `/preferences/{actorId}`
**Purpose**: Store user preferences and pet care choices
**Examples**:
- Food brand preferences (grain-free, natural, specific brands)
- Feeding schedule preferences
- Supplement preferences
- Budget considerations

### `/facts/{actorId}`
**Purpose**: Store factual information about pets and their needs
**Examples**:
- Pet details (name, breed, age, weight, activity level)
- Health conditions and dietary restrictions
- Previous veterinary recommendations
- Feeding history and responses

### `/summaries/{actorId}/{sessionId}`
**Purpose**: Store session summaries for context continuity
**Examples**:
- Key topics discussed in previous sessions
- Decisions made about pet care
- Follow-up items or recommendations given

## 🚨 Important Notes

### Session Management
- **One agent per session**: Only create one agent instance per session_id
- **Consistent actor_id**: Use the same actor_id across sessions for the same user
- **Agent caching**: The implementation caches agents to maintain memory consistency

### Memory Strategies
- Memory strategies must be configured in your AgentCore Memory resource
- Each strategy writes to specific namespaces
- Retrieval configuration determines which memories are loaded during conversations

### Best Practices
- Use meaningful session_id and actor_id values
- Configure appropriate relevance_score thresholds for your use case
- Test with different top_k values to optimize retrieval performance
- Monitor CloudWatch logs for memory operation insights

## 🔗 Related Documentation

- [Strands Agents Documentation](https://github.com/strands-agents/strands)
- [AgentCore Memory Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)
- [Memory Strategies Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory-strategies.html)