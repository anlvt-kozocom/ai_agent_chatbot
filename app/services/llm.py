import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_llm(temperature: float = 0.7, model: str = os.getenv("GOOGLE_MODEL")):
    """
    Factory function to get an LLM instance.
    Infrastructure layer: Handles API keys and provider details.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        # For demonstration, we might warn or error. 
        # In production, ensure this is handled.
        print("Warning: GOOGLE_API_KEY is not set.")
        pass
        
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        google_api_key=api_key,
    )
