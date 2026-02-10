import logging
import traceback
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from vp_core.logging.context import get_log_context


class LogEntry(BaseModel):
    timestamp: datetime
    level: str
    request_id: str | None = None
    org_id: str | None = None
    ip: str | None = None
    message: str
    extra: dict[str, Any] | None = None
    lead_id: str | None = None


class PydanticJSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        context = get_log_context()
        extra = self.get_extra_fields(record)
        if record.exc_info:
            extra["exc_info"] = self.format_exception(record.exc_info)
        log_entry = LogEntry(
            timestamp=datetime.now(),
            level=record.levelname,
            request_id=context.get("request_id"),
            org_id=context.get("org_id"),
            lead_id=context.get("lead_id"),
            ip=context.get("ip"),
            message=record.getMessage(),
            extra=extra,
        )

        return log_entry.model_dump_json(indent=4)

    def get_extra_fields(self, record: logging.LogRecord) -> dict[str, Any]:
        extra_fields: dict[str, Any] = record.__dict__.copy()
        extra_fields.pop("args", None)
        extra_fields.pop("message", None)
        extra_fields.pop("levelname", None)
        extra_fields.pop("levelno", None)
        extra_fields.pop("name", None)
        extra_fields.pop("module", None)
        extra_fields.pop("lineno", None)
        extra_fields.pop("funcName", None)
        extra_fields.pop("created", None)
        extra_fields.pop("msecs", None)
        extra_fields.pop("exc_info", None)
        extra_fields.pop("stack_info", None)

        for key, value in extra_fields.items():
            if not isinstance(
                value, str | int | float | bool | list | dict | type(None)
            ):
                extra_fields[key] = str(value)

        return extra_fields

    def format_exception(self, exc_info: Any) -> str:
        stack_trace = traceback.format_exception(*exc_info)
        filtered_trace = [
            line
            for line in "".join(stack_trace).split("\n")
            if "/Users/hari/Documents/ror/oxo-agent/" in line
            or 'File "<string>"' in line
            or "Traceback (most recent call last):" in line
        ]
        return "\n".join(filtered_trace)


def setup_logger(
    log_level: int = logging.INFO, log_group: str = "oxo_agent"
) -> logging.Logger:
    logger = logging.getLogger(log_group)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setFormatter(PydanticJSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(log_level)
        logger.propagate = False

    return logger
