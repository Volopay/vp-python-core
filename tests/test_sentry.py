import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Request
from fastapi.responses import JSONResponse

from vp_core.logging.middleware import logging_middleware
from vp_core.logging_config import setup_logging


def test_setup_logging_with_sentry():
    with patch("sentry_sdk.init") as mock_sentry_init:
        with patch.dict(os.environ, {"SENTRY_DSN": "https://example.com"}):
            setup_logging()
            mock_sentry_init.assert_called_once()
            args, kwargs = mock_sentry_init.call_args
            assert kwargs["dsn"] == "https://example.com"


@pytest.mark.asyncio
async def test_logging_middleware_captures_exception():
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/test"
    mock_request.method = "GET"
    mock_request.headers = {}
    mock_request.client = MagicMock()
    mock_request.client.host = "127.0.0.1"

    async def mock_call_next(request):
        raise ValueError("Test Exception")

    with patch("sentry_sdk.capture_exception") as mock_capture:
        response = await logging_middleware(mock_request, mock_call_next)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        mock_capture.assert_called_once()
        args, _ = mock_capture.call_args
        assert isinstance(args[0], ValueError)
        assert str(args[0]) == "Test Exception"
        assert isinstance(args[0], ValueError)
        assert str(args[0]) == "Test Exception"
        assert str(args[0]) == "Test Exception"
