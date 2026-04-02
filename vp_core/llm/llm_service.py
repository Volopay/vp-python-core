from typing import Any, Type

from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from vp_core.helpers.parse_json import parse_llm_output
from vp_core.logging.logger import setup_logger

from .gemini_service import GEMINI_PRIMARY_MODEL, GeminiService
from .openai_service import OpenaiService

logger = setup_logger()


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

    async def with_structured_output(
        self,
        prompt: Any,
        response_model: Type[BaseModel],
        multiplier: float = 0.5,
        min_wait: float = 0.5,
        max_wait: float = 2,
        **kwargs
    ) -> Any:
        llm = self.llm(**kwargs)
        structured_llm = llm.with_structured_output(response_model, include_raw=True)

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=multiplier, min=min_wait, max=max_wait),
            reraise=True,
            before_sleep=lambda retry_state: logger.warning(
                f"Retrying LLM call due to error: {retry_state.outcome.exception() if retry_state.outcome else 'Unknown'}. "
                f"Attempt {retry_state.attempt_number}/3"
            ),
        )
        async def _execute():
            return await structured_llm.ainvoke(prompt)

        response = await _execute()

        if response is None:
            logger.error("LLM returned None")
            return {
                "status": "FAIL",
                "reason": "LLM failed to provide a structured result.",
            }

        parsed = response.get("parsed")
        raw = response.get("raw")

        if parsed is None:
            logger.error(f"LLM failed to parse structured output. Raw response: {raw}")
            return {
                "status": "FAIL",
                "reason": "LLM failed to provide a structured result.",
            }

        if hasattr(parsed, "model_dump"):
            return parsed.model_dump()

        return parsed
