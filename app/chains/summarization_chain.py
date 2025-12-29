from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.prompts.summarization_prompts import SUMMARIZATION_SYSTEM_PROMPT
from app.services.llm import get_llm


def build_summarization_chain():
    """
    Constructs the chain for summarization.
    """
    llm = get_llm(temperature=0.3)  # Low temp for factual summary

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SUMMARIZATION_SYSTEM_PROMPT),
            ("human", "{text}"),
        ]
    )

    return prompt | llm | StrOutputParser()
