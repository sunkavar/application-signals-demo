#!/usr/bin/env python3
"""
Test script for the enhanced nutrition agent with Strands AgentCore Memory integration.

This script demonstrates:
1. Creating an agent with AgentCore Memory
2. Multiple conversation turns with memory persistence
3. Long-term memory retrieval across sessions
4. Live API integration for supplement recommendations

Prerequisites:
- Set BEDROCK_AGENTCORE_MEMORY_ID environment variable
- Ensure the memory resource has the required strategies configured
- AWS credentials configured for Bedrock AgentCore
"""

import asyncio
import os
from datetime import datetime
from nutrition_agent import create_nutrition_agent

# Test configuration
MEMORY_ID = os.getenv("BEDROCK_AGENTCORE_MEMORY_ID", "nutrition_agent_mem-H98fg06LsS")
TEST_ACTOR_ID = f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
TEST_SESSION_ID = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

async def test_memory_integration():
    """Test the nutrition agent with AgentCore Memory integration"""
    
    print("🧪 Testing Nutrition Agent with Strands AgentCore Memory Integration")
    print(f"Memory ID: {MEMORY_ID}")
    print(f"Actor ID: {TEST_ACTOR_ID}")
    print(f"Session ID: {TEST_SESSION_ID}")
    print("-" * 60)
    
    # Create agent with memory
    agent = create_nutrition_agent(
        session_id=TEST_SESSION_ID,
        actor_id=TEST_ACTOR_ID
    )
    
    # Test conversation 1: Establish user preferences
    print("\n🗣️ Conversation 1: Establishing user preferences")
    response1 = await agent.async_invoke(
        "Hi! I have a 3-year-old Golden Retriever named Max who weighs 65 pounds. "
        "He's very active and I prefer natural, grain-free foods. "
        "Can you give me feeding guidelines?"
    )
    print(f"Agent: {response1}")
    
    # Test conversation 2: Ask about supplements (should use live API)
    print("\n🗣️ Conversation 2: Supplement recommendations (live API)")
    response2 = await agent.async_invoke(
        "What supplements would be good for Max? He's been a bit low energy lately."
    )
    print(f"Agent: {response2}")
    
    # Test conversation 3: Reference previous information
    print("\n🗣️ Conversation 3: Reference previous pet information")
    response3 = await agent.async_invoke(
        "Should I change Max's feeding schedule as he gets older?"
    )
    print(f"Agent: {response3}")
    
    print("\n✅ Memory integration test completed!")
    print("The agent should have:")
    print("- Remembered Max's details (name, breed, weight, age)")
    print("- Stored your preference for natural, grain-free foods")
    print("- Used live API data for supplement recommendations")
    print("- Referenced previous conversation context")

async def test_cross_session_memory():
    """Test memory persistence across different sessions"""
    
    print("\n🔄 Testing Cross-Session Memory Persistence")
    print("-" * 60)
    
    # Create a new session with the same actor
    new_session_id = f"test_session_2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    agent2 = create_nutrition_agent(
        session_id=new_session_id,
        actor_id=TEST_ACTOR_ID  # Same actor, different session
    )
    
    print(f"New Session ID: {new_session_id}")
    print(f"Same Actor ID: {TEST_ACTOR_ID}")
    
    # Test if agent remembers user preferences from previous session
    response = await agent2.async_invoke(
        "I'm back! Can you remind me what you know about my dog and my food preferences?"
    )
    print(f"Agent: {response}")
    
    print("\n✅ Cross-session memory test completed!")
    print("The agent should have retrieved:")
    print("- User preferences from /preferences/{actorId} namespace")
    print("- Pet facts from /facts/{actorId} namespace")
    print("- Previous session summaries if available")

if __name__ == "__main__":
    if not MEMORY_ID:
        print("❌ Error: BEDROCK_AGENTCORE_MEMORY_ID environment variable not set")
        print("Please set it to your AgentCore Memory resource ID")
        exit(1)
    
    print("🚀 Starting Strands AgentCore Memory Integration Tests")
    
    # Run the tests
    asyncio.run(test_memory_integration())
    asyncio.run(test_cross_session_memory())
    
    print("\n📝 Notes:")
    print("- Memory strategies should be configured in your AgentCore Memory resource")
    print("- Required strategies: summaryMemoryStrategy, userPreferenceMemoryStrategy, semanticMemoryStrategy")
    print("- Check AWS CloudWatch logs for detailed memory operation logs")