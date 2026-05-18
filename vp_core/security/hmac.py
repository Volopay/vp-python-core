"""
HMAC request signing utilities for service-to-service authentication.

Pure-function helpers for signing and verifying HTTP requests between
Volopay microservices. Shared across all Python services that need
Layer 1 (backend-to-backend) auth.

Usage (verifier side — e.g., volo-agents FastAPI dependency):

    from vp_core.security import verify_request

    body = await request.body()
    ok = verify_request(
        secret=SHARED_SECRET,
        signature=request.headers["x-signature"],
        method=request.method,
        path=request.url.path,
        body=body,
        timestamp=int(request.headers["x-timestamp"]),
    )

Usage (sender side — if the sender is Python):

    from vp_core.security import sign_request

    signature, ts = sign_request(SHARED_SECRET, "POST", "/api/v1/x", body_bytes)
    headers = {"X-Signature": signature, "X-Timestamp": str(ts)}

Non-Python senders (e.g., the Ruby volo-be client) implement their own
signing using OpenSSL::HMAC. The shared test vector in tests/test_hmac.py
enforces byte-identical output across languages.
"""

import hashlib
import hmac
import time

REPLAY_WINDOW_SECONDS = 60


def sign_request(
    secret: str,
    method: str,
    path: str,
    body: bytes,
    timestamp: int | None = None,
) -> tuple[str, int]:
    """
    Compute HMAC-SHA256 signature over (timestamp, method, path, body).

    Args:
        secret: Shared secret known to both sender and verifier
        method: HTTP method (case-insensitive, normalized to uppercase)
        path: Request path (e.g., "/api/v1/keywords/suggest")
        body: Raw request body bytes (empty bytes for GET requests)
        timestamp: Unix timestamp in seconds. If None, uses current time.

    Returns:
        (signature_hex, timestamp) — both travel as headers.
    """
    ts = timestamp if timestamp is not None else int(time.time())
    prefix = f"{ts}\n{method.upper()}\n{path}\n".encode()
    signature = hmac.new(secret.encode(), prefix + body, hashlib.sha256).hexdigest()
    return signature, ts


def verify_request(
    secret: str,
    signature: str,
    method: str,
    path: str,
    body: bytes,
    timestamp: int,
    window_seconds: int = REPLAY_WINDOW_SECONDS,
) -> bool:
    """
    Verify an incoming HMAC signature with replay protection.

    Performs two checks:
    1. Timestamp is within ``window_seconds`` of now (replay protection)
    2. Recomputed signature matches the provided one (timing-safe)

    Args:
        secret: Shared secret known to both sender and verifier
        signature: Hex-encoded signature from X-Signature header
        method: HTTP method from the incoming request
        path: Request path from the incoming request
        body: Raw request body bytes
        timestamp: Unix timestamp from X-Timestamp header
        window_seconds: Max allowed clock drift. Defaults to 60s.

    Returns:
        True if valid, False on any failure (timestamp skew, signature
        mismatch, wrong secret). Never raises.
    """
    if abs(int(time.time()) - timestamp) > window_seconds:
        return False

    expected, _ = sign_request(secret, method, path, body, timestamp)
    return hmac.compare_digest(signature, expected)
