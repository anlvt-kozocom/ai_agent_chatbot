from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.prompts.extraction_prompts import EXTRACTION_SYSTEM_PROMPT
from app.services.llm import get_llm
from typing import TypedDict, Optional, List


class Requirements(TypedDict, total=False):
    """Extracted phone requirements. All fields are optional."""

    price: Optional[str]
    usage: Optional[List[str]]  # Changed from str to List[str] for multi-usage
    brand: Optional[str]
    phone_type: Optional[str]  # New field for device type
    ram: Optional[str]
    storage: Optional[str]
    color: Optional[str]
    specs: Optional[str]
    num_products: Optional[int]


def build_extraction_chain():
    """
    Chain to extract requirements from text.
    Returns a dict.
    """
    llm = get_llm(temperature=0)

    # Use JsonOutputParser for reliable extraction
    # Note: with_structured_output was causing caching/incorrect results
    parser = JsonOutputParser()

    prompt = ChatPromptTemplate.from_template(EXTRACTION_SYSTEM_PROMPT)
    return prompt | llm | parser
