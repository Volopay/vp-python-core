import logging
import os
import traceback
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from vp_core.logging.context import get_log_context


class LogEntry(BaseModel):
    timestamp: datetime
    level: str
    request_id: Optional[str] = None
    org_id: Optional[str] = None
    ip: Optional[str] = None
    message: str
    extra: Optional[dict] = None
    lead_id: Optional[str] = None


class PydanticJSONFormatter(logging.Formatter):
    def format(self, record):
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

        is_dev = os.getenv("ENVIRONMENT", "dev").lower() == "dev"
        if is_dev:
            return log_entry.model_dump_json(indent=4)
        return log_entry.model_dump_json()

    def get_extra_fields(self, record):
        extra_fields = record.__dict__.copy()
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
            if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                extra_fields[key] = str(value)

        return extra_fields

    def format_exception(self, exc_info):
        stack_trace = traceback.format_exception(*exc_info)
        cwd = os.getcwd()

        filtered_trace = [
            line
            for line in "".join(stack_trace).split("\n")
            if "/app/" in line
            or cwd in line
            or 'File "<string>"' in line
            or "Traceback (most recent call last):" in line
        ]
        return "\n".join(filtered_trace)


def setup_logger(log_level=logging.INFO, log_group: str = "oxo_agent"):
    logger = logging.getLogger(log_group)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setFormatter(PydanticJSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(log_level)
        logger.propagate = False

    return logger
