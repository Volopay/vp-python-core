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
    request_id: str | None,
    org_id: str | None,
    lead_id: str | None,
    ip: str | None,
) -> None:
    request_id_var.set(request_id)
    org_id_var.set(org_id)
    lead_id_var.set(lead_id)
    ip_var.set(ip)


def get_log_context() -> dict[str, Any]:
    return {
        "request_id": request_id_var.get(),
        "org_id": org_id_var.get(),
        "lead_id": lead_id_var.get(),
        "ip": ip_var.get(),
    }
