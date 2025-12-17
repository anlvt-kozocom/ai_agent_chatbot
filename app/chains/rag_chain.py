from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from app.services.llm import get_llm
from app.prompts.rag_prompts import RAG_PROMPT, format_docs

def get_rag_chain(retriever):
    """
    Creates a RAG chain using the provided retriever.
    """
    llm = get_llm()
    
    return (
        {
            "context": RunnableLambda(
                lambda q: format_docs(retriever.invoke(q))
            ),
            "question": RunnablePassthrough()
        }
        | RAG_PROMPT
        | llm
    )


