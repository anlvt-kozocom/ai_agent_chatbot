from typing import Dict, Any

# Simple in-memory store: {thread_id: {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}}
THREAD_USAGE: Dict[str, Dict[str, int]] = {}


def increment_usage(thread_id: str, usage_metrics: Dict[str, int]):
    """
    Updates the token usage for a specific thread.
    """
    if thread_id not in THREAD_USAGE:
        THREAD_USAGE[thread_id] = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
        }

    current = THREAD_USAGE[thread_id]
    current["total_tokens"] += usage_metrics.get("total_tokens", 0)
    current["prompt_tokens"] += usage_metrics.get("prompt_tokens", 0)
    current["completion_tokens"] += usage_metrics.get("completion_tokens", 0)


def get_thread_usage(thread_id: str) -> Dict[str, int]:
    """
    Returns the accumulated usage for a thread.
    """
    return THREAD_USAGE.get(
        thread_id, {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}
    )
