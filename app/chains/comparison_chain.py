from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.prompts.comparison_prompts import COMPARISON_SYSTEM_PROMPT
from app.services.llm import get_llm


def build_comparison_chain():
    """
    Constructs the chain for product comparisons.
    Chain input:
    - context: str (retrieved info)
    - question: str
    - language: str
    """
    llm = get_llm(temperature=0.3)  # Low temp for accurate comparisons

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", COMPARISON_SYSTEM_PROMPT),
            ("human", "{question}"),
        ]
    )

    return prompt | llm | StrOutputParser()
