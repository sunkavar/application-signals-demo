# Nutrition Agent with AgentCore Memory

## 🧠 AgentCore Memory Integration

The nutrition agent now includes **AgentCore Memory** for persistent conversation context and personalized recommendations.

### Memory Features:
- **Remembers pet information** across conversations (names, breeds, ages, weights, health conditions)
- **Stores user preferences** for supplements, feeding schedules, and dietary restrictions
- **Maintains conversation history** for context-aware responses
- **Personalizes recommendations** based on previous interactions

### Memory Configuration:
- **Memory ID**: `nutrition_agent_mem-H98fg06LsS` (your existing memory)
- **Namespaces**:
  - `/users/{actor_id}/preferences` - User dietary preferences and supplement choices
  - `/users/{actor_id}/facts` - Pet information and health conditions
  - `/users/{actor_id}/pets` - Specific pet details and characteristics

### Environment Variables:
```bash
export BEDROCK_AGENTCORE_MEMORY_ID=nutrition_agent_mem-H98fg06LsS
export AWS_REGION=us-west-2
```

## 🔄 Live API Integration

The agent calls the live nutrition service API for current nutrition facts:
- **API Endpoint**: `http://aeb5c47baeace494bbf21a47d352baf7-1656987644.us-west-2.elb.amazonaws.com/api/nutrition/facts/{pet_type}`
- **Always fetches live data** before providing supplement recommendations
- **Combines live nutrition facts** with personalized memory for optimal advice

## 🎯 Error Simulation

- **10% chance** of random error on each request (roughly 1 in 10 requests)
- **Error types**: TimeoutException, ValidationException, ServiceException, RateLimitException, NetworkException

## 🧪 Testing

### Test Memory Integration:
```bash
python test_memory_integration.py
```

### Test Live API Integration:
```bash
python test_live_api.py
```

### Example Conversation Flow:
1. **User**: "I have a 5-year-old golden retriever named Max who weighs 70 pounds"
2. **Agent**: Remembers Max's details in memory
3. **User**: "What omega-3 supplements would you recommend?"
4. **Agent**: 
   - Calls live nutrition service for dog nutrition facts
   - Provides personalized omega-3 advice for Max based on his breed/weight
   - Stores supplement preferences in memory
5. **User**: "How much should I feed him?"
6. **Agent**: Uses remembered information about Max (70 lbs, golden retriever) for feeding guidelines

## 🚀 Deployment

The agent is now enhanced with:
- ✅ **AgentCore Memory** for personalization
- ✅ **Live nutrition service** integration
- ✅ **Error simulation** for testing
- ✅ **Session management** for conversation continuity

Deploy with your existing AgentCore setup - the memory integration will automatically activate when the `BEDROCK_AGENTCORE_MEMORY_ID` environment variable is set.