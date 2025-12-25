from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.prompts.extraction_prompts import EXTRACTION_SYSTEM_PROMPT
from app.services.llm import get_llm
from typing import TypedDict, Optional


class Requirements(TypedDict):
    price: Optional[str]
    usage: Optional[str]
    brand: Optional[str]
    specs: Optional[str]


def build_extraction_chain():
    """
    Chain to extract requirements from text.
    Returns a dict.
    """
    llm = get_llm(temperature=0)

    prompt = ChatPromptTemplate.from_template(EXTRACTION_SYSTEM_PROMPT)
    parser = JsonOutputParser(pydantic_object=Requirements)

    return prompt | llm | parser
