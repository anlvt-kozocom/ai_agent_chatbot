import unittest
import asyncio
from typing import Dict, Any
from app.services.memory_service import (
    update_working_memory,
    compress_context,
    get_empty_working_memory,
    get_empty_summary_memory,
)
from app.models.schemas import AgentState
from langchain_core.messages import HumanMessage, AIMessage


class TestMemoryService(unittest.TestCase):
    def test_update_working_memory_freeze(self):
        state: AgentState = {"working_memory": get_empty_working_memory()}

        # 1. Update with high confidence
        new_info = {
            "intent": "RECOMMENDATION",
            "confidence": 0.9,
            "updates": {"budget_range": {"min": 0, "max": 100}},
        }

        wm = asyncio.run(update_working_memory(state, new_info))

        self.assertEqual(wm["intent"], "RECOMMENDATION")
        self.assertTrue(wm["intent_frozen"])
        self.assertEqual(wm["budget_range"], {"min": 0, "max": 100})

        # 2. Try to update intent again (should be frozen)
        state["working_memory"] = wm
        new_info_2 = {
            "intent": "GENERAL",
            "confidence": 0.5,
            "updates": {"usage_context": ["gaming"]},
        }

        wm2 = asyncio.run(update_working_memory(state, new_info_2))

        self.assertEqual(wm2["intent"], "RECOMMENDATION")  # Should remain frozen
        self.assertEqual(wm2["usage_context"], ["gaming"])  # Should update constraints

    def test_compress_context(self):
        wm = get_empty_working_memory()
        wm["intent"] = "PRODUCT_INFO"
        wm["specific_products"] = ["iPhone 15"]

        sm = get_empty_summary_memory()
        sm["summary_text"] = "User asked about phones."
        sm["key_decisions"] = ["User prefers Apple"]

        messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there"),
            HumanMessage(content="Tell me about iPhone 15"),
        ]

        state: AgentState = {
            "working_memory": wm,
            "summary_memory": sm,
            "messages": messages,
        }

        context_str = compress_context(state)

        # Verify content
        self.assertIn("PREVIOUS CONTEXT: User asked about phones.", context_str)
        self.assertIn("DECISIONS: User prefers Apple", context_str)
        self.assertIn('CURRENT STATE: {"intent": "PRODUCT_INFO"', context_str)
        self.assertIn("iPhone 15", context_str)
        self.assertIn("RECENT CHAT:", context_str)
        self.assertIn("HUMAN: Tell me about iPhone 15", context_str)


if __name__ == "__main__":
    unittest.main()
