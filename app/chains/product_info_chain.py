from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from app.prompts.product_info_prompts import PRODUCT_INFO_SYSTEM_PROMPT
from app.services.llm import get_llm


def build_product_info_chain():
    """
    Constructs the chain for product information (RAG).
    Chain input:
    - context: str (retrieved info)
    - question: str
    - history: List[BaseMessage]
    """
    llm = get_llm(temperature=0.3)  # Low temp for factual info

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", PRODUCT_INFO_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )

    return prompt | llm | StrOutputParser()
