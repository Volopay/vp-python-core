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
        "bootstrap.servers": kafka_brokers,
        "retry.backoff.ms": kwargs.get("retry_backoff_ms") or 1000,
    }

    if not is_consumer:
        config["request.timeout.ms"] = kwargs.get("request_timeout_ms") or 60000

    if is_consumer:
        config.update(
            {
                "group.id": kafka_group_id,
                "auto.offset.reset": kwargs.get("auto_offset_reset") or "earliest",
                "enable.auto.commit": kwargs.get("enable_auto_commit") or False,
                "max.poll.interval.ms": kwargs.get("max_poll_interval_ms") or 500000,
                "heartbeat.interval.ms": kwargs.get("heartbeat_interval_ms") or 5000,
            }
        )

    if kafka_username and kafka_password:
        config.update(
            {
                "security.protocol": "SASL_PLAINTEXT",
                "sasl.mechanism": "SCRAM-SHA-512",
                "sasl.username": kafka_username,
                "sasl.password": kafka_password,
            }
        )

    return config
