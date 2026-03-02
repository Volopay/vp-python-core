from typing import Any

from vp_core.helpers.parse_json import parse_llm_output

from .gemini_service import GEMINI_PRIMARY_MODEL, GeminiService
from .openai_service import OpenaiService


class LlmService:
    CURRENT_LLM = "gemini"

    def llm(self, model=GEMINI_PRIMARY_MODEL) -> Any:
        return self._service(model=model)

    def parse_json_output(self, output: str) -> Any:
        return parse_llm_output(output)

    # --- private methods ----

    def _service(self, model=GEMINI_PRIMARY_MODEL):
        if self.CURRENT_LLM == "gemini":
            return GeminiService().llm(model=model)
        elif self.CURRENT_LLM == "openai":
            return OpenaiService().llm()
        else:
            return GeminiService().llm(model=model)
