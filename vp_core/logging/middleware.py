import time
import uuid
from collections.abc import Awaitable, Callable

import sentry_sdk
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from vp_core.logging.context import set_log_context
from vp_core.logging_config import get_logger

logger = get_logger(__name__)


async def logging_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    # Skip logging for the ping endpoint
    if request.url.path == "/_ping":
        return await call_next(request)

    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Get client IP address
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.client.host if request.client else "Unknown"

    set_log_context(request_id=request_id, org_id=None, lead_id=None, ip=ip)

    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={"request_id": request_id},
    )

    try:
        response: Response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(
            f"""Request finished in {process_time:.4f}s: {request.method} {request.url.path}""",
            extra={"request_id": request_id, "status_code": response.status_code},
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"""Request failed in {process_time:.4f}s: {request.method} {request.url.path} - {e}""",
            extra={"request_id": request_id},
            stack_info=True,
            stacklevel=1,
            exc_info=True,
        )
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error"},
        )
