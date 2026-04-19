"""
Volopay Backend (volo-be) HTTP client utilities.

This module provides shared utilities for microservices that need to interact
with the main volo-be backend, primarily for auth token validation.

Usage:
    from vp_core.clients.volopay_be import validate_token

    valid = await validate_token(
        client="web",
        access_token="abc123",
        uid="user@example.com",
        account="volopay",
        volo_be_url="https://api.volopay.com"
    )
"""

import httpx


async def validate_token(
    client: str,
    access_token: str,
    uid: str,
    account: str,
    volo_be_url: str,
    x_feature: str | None = None,
) -> bool:
    """
    Validates a user's session token by calling volo-be's token validation endpoint.

    This is used by satellite microservices (volo-agents, ocr-reader, etc.) to verify
    that a frontend user's token is valid without maintaining their own user database.

    Note: Environment-specific logic (e.g., skipping validation in test) should be
    handled by the calling service, not here. This is a pure HTTP client function.

    Args:
        client: Client identifier (e.g., "web", "mobile")
        access_token: User's session access token
        uid: User identifier (typically email)
        account: Account/organization identifier
        volo_be_url: Base URL of volo-be (e.g., "https://api.volopay.com")
        x_feature: Optional feature flag header

    Returns:
        True if the token is valid (volo-be returned 200), False otherwise.

    Example:
        >>> valid = await validate_token(
        ...     client="web",
        ...     access_token="eyJ0eXAi...",
        ...     uid="user@example.com",
        ...     account="volopay",
        ...     volo_be_url="https://api.volopay.com"
        ... )
        >>> if valid:
        ...     # proceed with authenticated request
    """
    headers = {
        "client": client,
        "access-token": access_token,
        "uid": uid,
        "account": account,
    }

    # Add optional x_feature header if provided
    if x_feature:
        headers["x_feature"] = x_feature

    async with httpx.AsyncClient(base_url=volo_be_url, headers=headers) as http:
        try:
            response = await http.get("/api/v3/auth/user/validate_token")
            return response.status_code == 200
        except httpx.HTTPError:
            # Network errors, timeouts, etc. — treat as invalid token
            return False


# Future: Two-layer auth builder
# When multiple microservices (volo-agents, ocr-reader, future services) all adopt
# the same two-layer auth pattern (shared secret + token validation fallback),
# consider adding a generic FastAPI dependency builder here:
#
# def create_two_layer_auth_dependency(
#     service_name: str,              # "agents", "ocr", etc.
#     secret_env_var: str,            # "VOLO_BE_AGENTS_SECRET"
#     volo_be_url_env_var: str = "VOLO_BE_URL",
#     env_var: str = "ENV"
# ) -> Callable:
#     """
#     Creates a FastAPI Depends() function that enforces two-layer auth:
#     1. Checks volo_be_{service_name}_secret header against env var
#     2. Falls back to validate_token() if Layer 1 fails
#
#     Returns:
#         A FastAPI dependency (Depends-compatible callable)
#
#     Example:
#         from vp_core.clients import create_two_layer_auth_dependency
#
#         AuthDep = create_two_layer_auth_dependency(
#             service_name="agents",
#             secret_env_var="VOLO_BE_AGENTS_SECRET"
#         )
#
#         app.include_router(router, dependencies=[AuthDep])
#     """
