from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel


class GeminiService:
    def llm(self, model="gemini-2.5-flash-lite") -> BaseChatModel:

        llm = init_chat_model(f"google_genai:{model}", temperature=0.5)
        return llm
