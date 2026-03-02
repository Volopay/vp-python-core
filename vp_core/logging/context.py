import contextvars
from typing import Any

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)
org_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "org_id", default=None
)
lead_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "lead_id", default=None
)
ip_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("ip", default=None)


def set_log_context(
    request_id: str | None = None,
    org_id: str | None = None,
    lead_id: str | None = None,
    ip: str | None = None,
) -> None:
    if request_id is not None:
        request_id_var.set(request_id)
    if org_id is not None:
        org_id_var.set(org_id)
    if lead_id is not None:
        lead_id_var.set(lead_id)
    if ip is not None:
        ip_var.set(ip)


def get_log_context() -> dict[str, Any]:
    return {
        "request_id": request_id_var.get(),
        "org_id": org_id_var.get(),
        "lead_id": lead_id_var.get(),
        "ip": ip_var.get(),
    }
