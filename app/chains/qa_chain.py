from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from app.prompts.qa_prompts import QA_SYSTEM_PROMPT
from app.services.llm import get_llm

def build_qa_chain():
    """
    Constructs the LCEL chain for Question Answering.
    Chains layer: Logic for combining Prompts + LLM.
    Updated to include MessagesPlaceholder for conversation history.
    """
    llm = get_llm(temperature=0.5)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", QA_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"), # Inject history here
        ("human", "{question}"),
    ])
    
    # Returns a Runnable that accepts {"question": str, "history": List[BaseMessage]} -> returns str
    return prompt | llm | StrOutputParser()
