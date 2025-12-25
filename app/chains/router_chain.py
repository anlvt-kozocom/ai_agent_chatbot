from langchain_core.output_parsers import StrOutputParser
from app.services.llm import get_llm
from app.prompts.router_prompts import ROUTER_PROMPT, GENERAL_CHAT_PROMPT


def get_router_chain():
    """
    Chain to classify user intent.
    """
    llm = get_llm(temperature=0)  # Low temperature for deterministic classification
    return ROUTER_PROMPT | llm | StrOutputParser()


def get_general_chat_chain():
    """
    Chain for general conversation.
    """
    llm = get_llm(temperature=0.7)
    return GENERAL_CHAT_PROMPT | llm | StrOutputParser()
