import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables
from langchain_openai import ChatOpenAI

# Load environment variables
# Load environment variables
load_dotenv(override=True)


def get_llm(temperature: float = 0.7, model: str = None):
    """
    Factory function to get an LLM instance.
    Infrastructure layer: Handles API keys and provider details.
    """
    provider = os.getenv("LLM_PROVIDER", "google").lower()
    if provider == "openai":
        # Check standard key first, then custom user key
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY (or OPEN_API_KEY) is not set.")

        # Default to gpt-3.5-turbo if OPENAI_MODEL is not set
        openai_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        return ChatOpenAI(model=openai_model, temperature=temperature, api_key=api_key)

    # Default to Google
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Warning: GOOGLE_API_KEY is not set.")

    google_model = model or os.getenv("GOOGLE_MODEL", "gemini-1.5-pro")

    return ChatGoogleGenerativeAI(
        model=google_model,
        temperature=temperature,
        google_api_key=api_key,
    )
