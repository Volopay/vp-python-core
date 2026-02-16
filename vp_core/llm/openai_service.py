from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from config import OPENAI_MODEL, OPENAI_TEMPERATURE


class OpenaiService:
    def llm(self) -> BaseChatModel:
        llm = init_chat_model(OPENAI_MODEL, temperature=OPENAI_TEMPERATURE)
        return llm
