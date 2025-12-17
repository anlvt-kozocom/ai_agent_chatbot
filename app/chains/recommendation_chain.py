from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.prompts.recommendation_prompts import RECOMMENDATION_SYSTEM_PROMPT
from app.services.llm import get_llm

def build_recommendation_chain():
    """
    Constructs the chain for product recommendations.
    Chain input:
    - requirements: str (formatted requirements)
    - context: str (retrieved product info)
    """
    llm = get_llm(temperature=0.5)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", RECOMMENDATION_SYSTEM_PROMPT),
        ("human", "My requirements are: {requirements}. Please recommend suitable products based on the provided context."),
    ])
    
    return prompt | llm | StrOutputParser()

