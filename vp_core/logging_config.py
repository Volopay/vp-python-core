import logging
import os
import sys

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from vp_core.logging.logger import PydanticJSONFormatter


def setup_logging(log_level: int = logging.INFO) -> None:
    # Initialize Sentry
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR,  # Send errors as events
        )
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                sentry_logging,
                FastApiIntegration(),
            ],
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            environment=os.getenv("ENVIRONMENT", "development"),
        )

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
