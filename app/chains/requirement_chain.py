from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from app.prompts.requirement_prompts import REQUIREMENT_SYSTEM_PROMPT
from app.services.llm import get_llm


def build_requirement_chain():
    """
    Constructs the chain for gathering user requirements.
    Chain input:
    - history: List[BaseMessage]
    - current_requirements: str (formatted list of requirements)
    """
    llm = get_llm(temperature=0.4)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", REQUIREMENT_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
        ]
    )

    return prompt | llm | StrOutputParser()
