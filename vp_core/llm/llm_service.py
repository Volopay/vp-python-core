from typing import Any

from llm.gemini_service import GeminiService
from llm.openai_service import OpenaiService

from vp_core.helpers.parse_json import parse_llm_output


class LlmService:
    CURRENT_LLM = "gemini"

    def llm(self, model="gemini-2.5-flash-lite") -> Any:
        return self._service(model=model)

    def parse_json_output(self, output: str) -> Any:
        return parse_llm_output(output)

    # --- private methods ----

    def _service(self, model="gemini-2.5-flash-lite"):
        if self.CURRENT_LLM == "gemini":
            return GeminiService().llm(model=model)
        elif self.CURRENT_LLM == "openai":
            return OpenaiService().llm()
        else:
            return GeminiService().llm(model=model)
