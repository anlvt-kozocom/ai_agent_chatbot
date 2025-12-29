import pytest
from unittest.mock import AsyncMock, MagicMock
from app.agents.context_resolution_agent import context_resolution_node
from app.models.schemas import AgentState
from langchain_core.messages import HumanMessage, AIMessage


@pytest.mark.asyncio
async def test_context_resolution_no_history():
    state = {"messages": [HumanMessage(content="Hello")]}
    result = await context_resolution_node(state, None)
    assert result["standalone_query"] == "Hello"


@pytest.mark.asyncio
async def test_context_resolution_with_history(mocker):
    # Mock the chain to avoid actual LLM calls
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = "Compare iPhone 15 and Galaxy S24"

    mocker.patch(
        "app.agents.context_resolution_agent.get_context_resolution_chain",
        return_value=mock_chain,
    )

    state = {
        "messages": [
            HumanMessage(content="Tell me about iPhone 15"),
            AIMessage(content="It is a great phone."),
            HumanMessage(content="Compare it with Galaxy S24"),
        ]
    }

    result = await context_resolution_node(state, None)

    assert result["standalone_query"] == "Compare iPhone 15 and Galaxy S24"
    mock_chain.ainvoke.assert_called_once()


# Manual run block if pytest not available or for quick check
if __name__ == "__main__":
    import asyncio

    async def run_test():
        print("Running Context Resolution Test...")

        # Test 1: No history
        state1 = {"messages": [HumanMessage(content="Hello")]}
        res1 = await context_resolution_node(state1, None)
        print(f"Test 1: {res1['standalone_query']} (Expected: Hello)")

        # Test 2: We can't easily mock without pytest-mock in main block,
        # so we rely on the fact that without mock it calls LLM (requires env vars).
        # We will skip Test 2 in main block to avoid API costs/errors if env not set.
        print("Done.")

    asyncio.run(run_test())
