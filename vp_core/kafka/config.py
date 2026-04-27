from typing import Any, Optional


def get_kafka_config(
    kafka_brokers: str,
    kafka_group_id: Optional[str] = None,
    kafka_username: Optional[str] = None,
    kafka_password: Optional[str] = None,
    is_consumer: bool = False,
    request_timeout_ms: int = 60000,
    retry_backoff_ms: int = 1000,
    auto_offset_reset: str = "earliest",
    enable_auto_commit: bool = False,
    max_poll_interval_ms: int = 500000,
    heartbeat_interval_ms: int = 5000,
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
        request_timeout_ms: The maximum time the client will wait for a response (default: 60000).
        retry_backoff_ms: The amount of time to wait before attempting to retry a failed request (default: 1000).
        auto_offset_reset: A string that defines what to do when there is no initial offset in Kafka (default: "earliest").
        enable_auto_commit: If true, the consumer's offset will be periodically committed in the background (default: False).
        max_poll_interval_ms: The maximum delay between invocations of poll() (default: 500000).
        heartbeat_interval_ms: The expected time between heartbeats to the consumer coordinator (default: 5000).
        **kwargs: Additional overrides for the configuration.

    Returns:
        A dictionary containing the Kafka configuration.
    """
    if is_consumer and not kafka_group_id:
        raise ValueError("kafka_group_id is required when is_consumer is True")

    config: dict[str, Any] = {
        "bootstrap_servers": kafka_brokers,
        "request_timeout_ms": request_timeout_ms,
        "retry_backoff_ms": retry_backoff_ms,
    }

    if is_consumer:
        config.update(
            {
                "group_id": kafka_group_id,
                "auto_offset_reset": auto_offset_reset,
                "enable_auto_commit": enable_auto_commit,
                "max_poll_interval_ms": max_poll_interval_ms,
                "heartbeat_interval_ms": heartbeat_interval_ms,
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

    return config | kwargs
