from typing import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from app.prompts.translation_prompts import TRANSLATION_SYSTEM_PROMPT, REVERSE_TRANSLATION_SYSTEM_PROMPT
from app.services.llm import get_llm

class TranslationOutput(TypedDict):
    original_language: str
    translated_text: str

def build_translation_chain():
    """
    Translates input to English and detects original language.
    """
    llm = get_llm(temperature=0)
    prompt = ChatPromptTemplate.from_template(TRANSLATION_SYSTEM_PROMPT)
    parser = JsonOutputParser(pydantic_object=TranslationOutput)
    
    return prompt | llm | parser

def build_reverse_translation_chain():
    """
    Translates English output back to original language.
    """
    llm = get_llm(temperature=0.5)
    prompt = ChatPromptTemplate.from_template(REVERSE_TRANSLATION_SYSTEM_PROMPT)
    
    return prompt | llm | StrOutputParser()


