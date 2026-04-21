import asyncio
from typing import Any

from aiokafka import AIOKafkaConsumer
from aiokafka.structs import TopicPartition

from vp_core.logging.logger import setup_logger

logger = setup_logger()


class KafkaWorker:
    def __init__(
        self,
        topic: str,
        handler: Any,
        config: dict[str, Any],
        # Adjust this value based on the available memory.
        # A good starting point is to assume each task consumes around 256MB.
        max_concurrent_tasks: int = 8,
    ):
        self.consumer = AIOKafkaConsumer(topic, **config)
        self.topic = topic
        self.handler = handler
        self.running = True
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async def _handle_message(self, msg):
        try:
            await self.handler(msg)
            tp = TopicPartition(msg.topic, msg.partition)
            offsets = {tp: msg.offset + 1}
            await self.consumer.commit(offsets)
        except Exception:
            logger.exception(f"Error processing message: {msg.value.decode()}")
        finally:
            self.semaphore.release()

    async def start(self):
        await self.consumer.start()
        logger.info(f"Subscribed to topic: {self.topic}")

        try:
            async for msg in self.consumer:
                await self.semaphore.acquire()
                asyncio.create_task(self._handle_message(msg))
        except Exception:
            logger.exception("Kafka error")
        finally:
            await self.consumer.stop()
            logger.info("Consumer closed.")
