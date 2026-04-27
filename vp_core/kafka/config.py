from typing import Any, Optional


def get_kafka_config(
    kafka_brokers: str,
    kafka_group_id: Optional[str] = None,
    kafka_username: Optional[str] = None,
    kafka_password: Optional[str] = None,
    is_consumer: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Generates a Kafka configuration dictionary for producers or consumers.

    Args:
        kafka_brokers: Comma-separated string of Kafka brokers.
        kafka_group_id: Kafka consumer group ID (required if is_consumer is True).
        kafka_username: SASL username (optional).
        kafka_password: SASL password (optional).
        is_consumer: Whether to include consumer-specific settings.
        **kwargs: Additional overrides for the configuration.

    Returns:
        A dictionary containing the Kafka configuration.
    """
    if is_consumer and not kafka_group_id:
        raise ValueError("kafka_group_id is required when is_consumer is True")

    config: dict[str, Any] = {
        "bootstrap_servers": kafka_brokers,
        "request_timeout_ms": kwargs.get("request_timeout_ms") or 60000,
        "retry_backoff_ms": kwargs.get("retry_backoff_ms") or 1000,
    }

    if is_consumer:
        config.update(
            {
                "group_id": kafka_group_id,
                "auto_offset_reset": kwargs.get("auto_offset_reset") or "earliest",
                "enable_auto_commit": kwargs.get("enable_auto_commit") or False,
                "max_poll_interval_ms": kwargs.get("max_poll_interval_ms") or 500000,
                "heartbeat_interval_ms": kwargs.get("heartbeat_interval_ms") or 5000,
            }
        )

    if kafka_username and kafka_password:
        config.update(
            {
                "security_protocol": "SASL_PLAINTEXT",
                "sasl_mechanism": "SCRAM-SHA-512",
                "sasl_plain_username": kafka_username,
                "sasl_plain_password": kafka_password,
            }
        )

    return config
