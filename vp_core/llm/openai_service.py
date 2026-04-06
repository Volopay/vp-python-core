import os

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))


class OpenaiService:
    def llm(self, model=OPENAI_MODEL) -> BaseChatModel:
        llm = init_chat_model(model, temperature=OPENAI_TEMPERATURE)
        return llm
