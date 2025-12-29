from typing import Any, Dict, List
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from app.services.usage_store import increment_usage


class TokenUsageHandler(BaseCallbackHandler):
    """
    Callback handler to track token usage per thread.
    """

    def __init__(self, thread_id: str):
        self.thread_id = thread_id

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        # Typically looking for 'token_usage' in llm_output
        if response.llm_output:
            # Standard LangChain/OpenAI format often puts it in 'token_usage'
            usage = response.llm_output.get("token_usage")
            if usage:
                increment_usage(self.thread_id, usage)
                return

        # Fallback: Sometimes individual generations have usage info
        # This is vendor specific.
        # For Google/Gemini, usage_metadata might be in generations[0][0].message.usage_metadata
        if response.generations:
            # Flatten generations (list of lists)
            flat_gens = [g for gen_list in response.generations for g in gen_list]
            for gen in flat_gens:
                if hasattr(gen, "message") and hasattr(gen.message, "usage_metadata"):
                    # Common standard for newer LangChain integration
                    meta = gen.message.usage_metadata
                    if meta:
                        # Normalize keys
                        normalized = {
                            "total_tokens": meta.get("total_tokens", 0)
                            or meta.get("total", 0),
                            "prompt_tokens": meta.get("input_tokens", 0)
                            or meta.get("prompt", 0),
                            "completion_tokens": meta.get("output_tokens", 0)
                            or meta.get("completion", 0),
                        }
                        if normalized["total_tokens"] > 0:
                            increment_usage(self.thread_id, normalized)
                            # Assuming usage is per batch/response, break if we found it
                            # (usually shared across generations in a single call, but check this)
                            return
