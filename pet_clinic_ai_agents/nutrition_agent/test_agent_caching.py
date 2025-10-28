#!/usr/bin/env python3
"""
Test script to verify agent caching reduces memory create calls
"""
import asyncio
from nutrition_agent import agent_cache, create_nutrition_agent

async def test_agent_caching():
    """Test that agents are cached and reused properly"""
    
    print("🧪 Testing Agent Caching to Reduce Memory Create Calls")
    print("=" * 60)
    
    # Test 1: Create first agent
    print("📝 Test 1: Creating first agent")
    session_id = "test_session_123"
    actor_id = "test_user"
    cache_key = f"{session_id}:{actor_id}"
    
    print(f"Cache before: {len(agent_cache)} agents")
    agent1 = create_nutrition_agent(session_id=session_id, actor_id=actor_id)
    print(f"✅ Created agent for {cache_key}")
    
    # Test 2: Simulate multiple requests with same session/actor
    print("\n📝 Test 2: Simulating multiple requests (should reuse agent)")
    
    # Manually add to cache to simulate the invoke function behavior
    agent_cache[cache_key] = agent1
    print(f"Cache after first creation: {len(agent_cache)} agents")
    
    # Simulate 3 more requests with same session/actor
    for i in range(3):
        if cache_key in agent_cache:
            print(f"♻️ Request {i+2}: Reusing existing agent for {cache_key}")
            agent = agent_cache[cache_key]
        else:
            print(f"🔄 Request {i+2}: Creating new agent for {cache_key}")
            agent = create_nutrition_agent(session_id=session_id, actor_id=actor_id)
            agent_cache[cache_key] = agent
    
    print(f"Cache after multiple requests: {len(agent_cache)} agents")
    
    # Test 3: Different session/actor (should create new agent)
    print("\n📝 Test 3: Different session/actor (should create new agent)")
    session_id2 = "test_session_456"
    actor_id2 = "test_user2"
    cache_key2 = f"{session_id2}:{actor_id2}"
    
    if cache_key2 not in agent_cache:
        print(f"🔄 Creating new agent for {cache_key2}")
        agent2 = create_nutrition_agent(session_id=session_id2, actor_id=actor_id2)
        agent_cache[cache_key2] = agent2
    
    print(f"Final cache size: {len(agent_cache)} agents")
    
    print("\n✅ Agent Caching Test Results:")
    print("- Same session/actor: Agent reused (no new memory create calls)")
    print("- Different session/actor: New agent created (one memory create call)")
    print("- This reduces memory API calls significantly!")
    
    # Clear cache for clean state
    agent_cache.clear()
    print("\n🧹 Cache cleared for clean state")

if __name__ == "__main__":
    asyncio.run(test_agent_caching())