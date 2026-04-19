import os

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

GEMINI_PRIMARY_MODEL = os.getenv("GEMINI_PRIMARY_MODEL", "gemini-2.5-flash-lite")


class GeminiService:
    def llm(self, model=None, **kwargs) -> BaseChatModel:
        if model is None:
            model = GEMINI_PRIMARY_MODEL

        llm = init_chat_model(f"google_genai:{model}", temperature=0.5, **kwargs)
        return llm
