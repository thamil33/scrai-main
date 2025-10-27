import pytest
import asyncio
from scrai_core.core.llm_provider_factory import get_chat_model_from_env
from scrai_core.agents.models import Agent
from scrai_core.events.bus import EventBus
from scrai_core.agents.cognition import CognitiveAgent
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.mark.asyncio
async def test_simple_llm_api_call():
    """
    Tests a simple LLM API call and response using the default LM proxy provider.
    This test actually makes a real API call to verify the LLM integration works.
    """
    # Skip this test if no LLM provider is configured
    if not os.getenv("LLM_PROVIDER"):
        pytest.skip("No LLM provider configured - skipping integration test")

    # Get the chat model from environment (this will make actual API call)
    llm = get_chat_model_from_env()

    # Test a simple prompt
    test_prompt = "Respond with just the word 'Hello' in JSON format: {\"message\": \"Hello\"}"

    # Make the actual API call
    response = await llm.ainvoke(test_prompt)

    # Verify we got a response
    assert response is not None
    assert hasattr(response, 'content')
    assert response.content is not None
    assert len(response.content.strip()) > 0

    # Verify the response contains expected content (basic check)
    response_text = response.content.lower()
    assert "hello" in response_text or "json" in response_text

    print(f"LLM Response: {response.content}")


@pytest.mark.asyncio
async def test_cognitive_agent_with_real_llm():
    """
    Tests the CognitiveAgent with a real LLM call to ensure end-to-end functionality.
    """
    # Skip this test if no LLM provider is configured
    if not os.getenv("LLM_PROVIDER"):
        pytest.skip("No LLM provider configured - skipping integration test")

    # Create a mock agent and event bus
    test_agent = Agent(id="test_llm_agent", name="TestLLMAgent", latitude=0.0, longitude=0.0)
    event_bus = EventBus()

    # Create cognitive agent (this will use real LLM)
    cognitive_agent = CognitiveAgent(test_agent, event_bus)

    # Test the reasoning step with a simple scenario
    test_state = {
        "agent_model": test_agent,
        "memories": [],
        "relevant_memories": [],
        "nearby_objects": [],
        "nearby_agents": [],
        "environmental_context": "Agent is at position 0,0. There are no objects or other agents nearby.",
        "next_action": None
    }

    # This will make a real LLM call
    reasoned_state = await cognitive_agent._reason(test_state)

    # Verify we got a valid action back
    assert reasoned_state["next_action"] is not None
    assert hasattr(reasoned_state["next_action"], 'action_type')
    assert reasoned_state["next_action"].action_type in ["move", "interact_with_object", "communicate"]
    assert hasattr(reasoned_state["next_action"], 'payload')
    assert reasoned_state["next_action"].payload is not None

    print(f"Agent decided on action: {reasoned_state['next_action'].action_type}")
    print(f"Action payload: {reasoned_state['next_action'].payload}")


@pytest.mark.asyncio
async def test_llm_provider_configuration():
    """
    Tests that the LLM provider factory correctly configures the model based on environment.
    """
    # Test that we can get a model without errors
    if not os.getenv("LLM_PROVIDER"):
        pytest.skip("No LLM provider configured - skipping configuration test")

    # This should not raise an exception
    llm = get_chat_model_from_env()

    # Verify we got a valid model
    assert llm is not None

    # Test that the model has the expected attributes
    assert hasattr(llm, 'ainvoke') or hasattr(llm, 'invoke')

    # Test a simple call to verify configuration
    test_prompt = "Say 'test successful' and nothing else."
    response = await llm.ainvoke(test_prompt)

    assert response is not None
    assert "test successful" in response.content.lower()

    print(f"Configuration test passed. Provider: {os.getenv('LLM_PROVIDER', 'default')}")
