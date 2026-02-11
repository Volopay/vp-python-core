from vp_core.helpers.case_converter import to_camel
from vp_core.logging_config import get_logger, setup_logging

try:
    from vp_core.logging.middleware import logging_middleware
except ImportError:
    logging_middleware = None

__version__ = "0.1.0"
__all__ = ["setup_logging", "get_logger", "to_camel", "logging_middleware"]
