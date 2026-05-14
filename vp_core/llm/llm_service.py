from typing import Any, Type

from langchain_core.messages import BaseMessage
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from vp_core.helpers.parse_json import parse_llm_output
from vp_core.logging.logger import setup_logger

from .gemini_service import GEMINI_PRIMARY_MODEL, GeminiService
from .openai_service import OpenaiService

logger = setup_logger()


class LlmService:
    def __init__(self, current_llm: str = "gemini"):
        self.CURRENT_LLM = current_llm

    def llm(self, model=GEMINI_PRIMARY_MODEL, **kwargs) -> Any:
        return self._service(model=model, **kwargs)

    def parse_json_output(self, output: str) -> Any:
        return parse_llm_output(output)

    # --- private methods ----

    def _service(self, model=GEMINI_PRIMARY_MODEL, **kwargs):

        if self.CURRENT_LLM == "openai":
            return OpenaiService().llm(model=model, **kwargs)

        return GeminiService().llm(model=model, **kwargs)

    def _parse_raw_content(
        self, raw: Any, response_model: Type[BaseModel]
    ) -> BaseModel | None:
        raw_content = getattr(raw, "content", None) if raw else None
        if not raw_content:
            return None
        try:
            return response_model.model_validate_json(raw_content)
        except Exception:
            return None

    async def with_structured_output(
        self,
        prompt: str | list[BaseMessage],
        response_model: Type[BaseModel],
        multiplier: float = 0.5,
        min_wait: float = 0.5,
        max_wait: float = 2,
        **kwargs,
    ) -> BaseModel | dict[str, str]:
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
            response = await structured_llm.ainvoke(prompt)

            if response is None:
                raise ValueError("LLM returned None")

            raw = response.get("raw")
            parsed = response.get("parsed") or self._parse_raw_content(
                raw, response_model
            )

            if parsed is None:
                raise ValueError(
                    f"LLM failed to parse structured output. Raw response: {raw}"
                )

            return parsed

        try:
            return await _execute()
        except Exception as e:
            logger.error(f"LLM call failed after retries: {str(e)}")
            return {
                "status": "FAIL",
                "reason": f"LLM failed to provide a structured result: {str(e)}",
            }
