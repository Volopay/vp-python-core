from typing import Any, Optional


def get_consumer_config(
    kafka_brokers: str,
    kafka_group_id: str,
    kafka_username: Optional[str] = None,
    kafka_password: Optional[str] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Generates a Kafka consumer configuration dictionary.

    Args:
        brokers: Comma-separated string of Kafka brokers.
        group_id: Kafka consumer group ID.
        username: SASL username (optional).
        password: SASL password (optional).
        **kwargs: Additional overrides for the consumer configuration.

    Returns:
        A dictionary containing the Kafka consumer configuration.
    """
    config: dict[str, Any] = {
        "bootstrap_servers": kafka_brokers,
        "group_id": kafka_group_id,
        "auto_offset_reset": "earliest",
        "enable_auto_commit": False,
        "max_poll_interval_ms": 500000,
        "heartbeat_interval_ms": 5000,
        "request_timeout_ms": 60000,
        "retry_backoff_ms": 1000,
    }

    if kafka_username and kafka_password:
        config.update(
            {
                "security_protocol": "SASL_PLAINTEXT",
                "sasl_mechanism": "SCRAM-SHA-512",
                "sasl_plain_username": kafka_username,
                "sasl_plain_password": kafka_password,
            }
        )

    # Allow for additional overrides
    config.update(kwargs)

    return config
