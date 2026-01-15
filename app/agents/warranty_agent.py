from app.models.schemas import AgentState
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from app.services.warranty_rag_service import warranty_rag_service
from app.services.llm import get_llm


# Warranty response prompt template
WARRANTY_RESPONSE_TEMPLATE = """You are a customer service representative for a mobile phone store.
Your task is to answer questions about the store's warranty and return policies based on the provided policy documents.

INSTRUCTIONS:
- Answer the question clearly and accurately based on the warranty policy context provided
- If answering in Vietnamese, use professional and friendly Vietnamese language
- If answering in English, use clear and professional English
- Reference specific policy sections when relevant
- If the question cannot be answered from the policy documents, say so politely
- Be helpful and customer-focused

LANGUAGE: {language}

POLICY CONTEXT:
{context}

CUSTOMER QUESTION: {question}

Please provide a clear and helpful answer:"""


async def warranty_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Warranty Agent Node: Handles warranty and return policy queries.
    Uses the separate warranty RAG service to retrieve policy information.
    """
    print("--- Entering Warranty Node ---")

    messages = state.get("messages", [])
    if not messages:
        return {"answer": "No question found."}

    # Get query and language
    query = state.get("standalone_query") or messages[-1].content
    language = state.get("language", "en")

    print(f"Warranty query: {query} (language: {language})")

    # Retrieve warranty documents
    try:
        warranty_docs = await warranty_rag_service.retrieve(
            query=query, language=language, top_k=4
        )

        print(f"Retrieved {len(warranty_docs)} warranty documents")

        # Format context from retrieved documents
        if warranty_docs:
            context = "\n\n".join(
                [
                    f"--- Document {i + 1} ---\n{doc.page_content}"
                    for i, doc in enumerate(warranty_docs)
                ]
            )
        else:
            context = "No warranty policy information found."

    except Exception as e:
        print(f"Error retrieving warranty documents: {e}")
        context = "Unable to retrieve warranty policy information."

    # Generate response using LLM
    try:
        llm = get_llm(temperature=0.3)

        prompt = ChatPromptTemplate.from_template(WARRANTY_RESPONSE_TEMPLATE)

        chain = prompt | llm

        response = await chain.ainvoke(
            {
                "question": query,
                "context": context,
                "language": "Vietnamese (vi)" if language == "vi" else "English (en)",
            },
            config=config,
        )

        answer = response.content

    except Exception as e:
        print(f"Error generating warranty response: {e}")
        if language == "vi":
            answer = "Xin lỗi, tôi không thể trả lời câu hỏi về chính sách bảo hành lúc này. Vui lòng thử lại sau."
        else:
            answer = "Sorry, I cannot answer warranty policy questions at this time. Please try again later."

    # Update path
    current_path = state.get("path") or []
    new_path = current_path + ["warranty_node"]

    return {
        "answer": answer,
        "path": new_path,
    }
