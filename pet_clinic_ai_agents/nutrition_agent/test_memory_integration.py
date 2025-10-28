#!/usr/bin/env python3
"""
Test script to verify AgentCore Memory integration with the nutrition agent
"""
import asyncio
from nutrition_agent import create_nutrition_agent

async def test_memory_integration():
    """Test that the agent remembers information across conversations"""
    
    print("🧠 Testing AgentCore Memory Integration")
    print("=" * 60)
    
    # Create agent with specific session and actor
    session_id = "test_session_123"
    actor_id = "test_user"
    agent = create_nutrition_agent(session_id=session_id, actor_id=actor_id)
    
    # Test conversation 1: Introduce pet information
    print("📝 Conversation 1: Introducing pet information")
    print("-" * 40)
    query1 = "I have a 5-year-old golden retriever named Max who weighs 70 pounds. He has some joint issues."
    
    print(f"User: {query1}")
    print("Agent: ", end="")
    async for event in agent.stream_async(query1):
        if 'data' in event:
            print(event['data'], end='', flush=True)
    print("\n" + "=" * 60)
    
    # Test conversation 2: Ask about supplements (should remember Max)
    print("📝 Conversation 2: Asking about supplements (should remember Max)")
    print("-" * 40)
    query2 = "What omega-3 supplements would you recommend for Max?"
    
    print(f"User: {query2}")
    print("Agent: ", end="")
    async for event in agent.stream_async(query2):
        if 'data' in event:
            print(event['data'], end='', flush=True)
    print("\n" + "=" * 60)
    
    # Test conversation 3: Follow-up question (should remember context)
    print("📝 Conversation 3: Follow-up question (should remember context)")
    print("-" * 40)
    query3 = "How much should I feed him daily?"
    
    print(f"User: {query3}")
    print("Agent: ", end="")
    async for event in agent.stream_async(query3):
        if 'data' in event:
            print(event['data'], end='', flush=True)
    print("\n" + "=" * 60)
    
    print("✅ Memory integration test completed!")
    print("Expected behavior:")
    print("- Agent should remember Max (golden retriever, 70 lbs, joint issues)")
    print("- Supplement recommendations should be personalized for Max")
    print("- Feeding guidelines should consider Max's weight and breed")

if __name__ == "__main__":
    asyncio.run(test_memory_integration())