from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.llm import get_llm
from langchain_core.runnables import Runnable

# System prompt for context resolution
CONTEXT_RESOLUTION_SYSTEM_PROMPT = """You are an expert at understanding conversation context.
Your task is to rewrite the user's latest question into a standalone question that fully captures the context from the conversation history.

Rules:
1. If the latest question contains pronouns like "it", "they", "that", "this", "the first one", "the second one", REPLACE them with the specific noun(s) they refer to from the history.
2. If the user asks for "more info" or "details" without specifying the subject, ADD the subject from the previous turn.
3. If the user asks a comparison question like "compare with B", and the previous topic was "A", rewrite it as "Compare A and B".
4. If the latest question is already standalone and clear, return it exactly as is.
5. DO NOT answer the question. ONLY rewrite it.
6. Keep the language of the rewritten question the SAME as the original question (e.g. if user asks in Vietnamese, rewrite in Vietnamese).

Examples:

History:
User: Tell me about iPhone 15.
AI: [Details about iPhone 15]

User: How much is it?
Standalone: How much is iPhone 15?

---
History:
User: Compare iPhone 15 and Galaxy S24.
AI: [Comparison table]

User: Which one is cheaper?
Standalone: Which one is cheaper between iPhone 15 and Galaxy S24?

---
History:
User: I want a phone for gaming.
AI: I recommend ASUS ROG Phone 8.

User: Compare it with Red Magic 9.
Standalone: Compare ASUS ROG Phone 8 with Red Magic 9.

---
History:
User: iPhone 15 specs.
AI: [Specs]

User: And iPhone 14?
Standalone: iPhone 14 specs.
"""


def get_context_resolution_chain(model_name: str = "gpt-4o-mini") -> Runnable:
    """
    Creates a chain that takes 'question' and 'history' and returns 'standalone_question'.
    """
    llm = get_llm(model=model_name, temperature=0.0)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CONTEXT_RESOLUTION_SYSTEM_PROMPT),
            ("human", "History:\n{history}\n\nUser: {question}\nStandalone:"),
        ]
    )

    chain = prompt | llm | StrOutputParser()
    return chain
