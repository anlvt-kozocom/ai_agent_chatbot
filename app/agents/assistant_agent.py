import os
from typing import List

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from app.prompts.system_prompt import SYSTEM_PROMPT

load_dotenv()

class AssistantAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyBbxQ2lVTJEVaW5rXwn3SH5C4WXINoNQMo")

        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        model_name = os.getenv("MODEL_NAME")
        # Initialize LLM - allows override via env vars
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.1, # Lower temperature for RAG consistency
            google_api_key=api_key
        )
        
        # System prompt inspired by llm_gemini.py
        self.system_prompt = SYSTEM_PROMPT

    async def agenerate_response(self, messages: List[dict], context: str = "") -> str:
        """
        Generate a response based on the conversation history.
        Args:
            messages: List of dicts with 'role' and 'content'
            context: Optional retrieved context string (RAG)
        Returns:
            str: The assistant's response content
        """
        # Convert dict messages to LangChain messages
        lc_messages: List[BaseMessage] = [SystemMessage(content=self.system_prompt)]
        
        for i, msg in enumerate(messages):
            if msg["role"] == "user":
                content = msg["content"]
                # Inject context into the last user message if provided
                if context and i == len(messages) - 1:
                    content = f"Based on the following context:\n{context}\nPlease answer the question: {content}"
                
                lc_messages.append(HumanMessage(content=content))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))
        
        # Invoke LLM
        response = await self.llm.ainvoke(lc_messages)
        
        return str(response.content)

