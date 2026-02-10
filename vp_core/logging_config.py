import logging
import sys

from vp_core.logging.logger import PydanticJSONFormatter


def setup_logging(log_level: int = logging.INFO) -> None:
    # Disable uvicorn's access logger
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.handlers = []
    uvicorn_access.propagate = False

    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicate logs
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    formatter = PydanticJSONFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Set the root logger's level
    logging.basicConfig(level=log_level, handlers=[handler])


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
