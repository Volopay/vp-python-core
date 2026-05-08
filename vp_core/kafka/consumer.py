import asyncio
import traceback
from typing import Any

from confluent_kafka import KafkaError, TopicPartition
from confluent_kafka.aio import AIOConsumer

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
        self.topic = topic
        self.handler = handler
        self.config = config
        self.running = True
        self.consumer: AIOConsumer | None = None
        self._semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self._queue: asyncio.Queue = asyncio.Queue()
        self._commit_lock = asyncio.Lock()
        self._live_tasks: set[asyncio.Task] = set()

    async def _handle_message(self, msg):
        """
        Internal method to process a single message and commit its offset safely.
        """
        tp = TopicPartition(msg.topic(), msg.partition())
        try:
            await self.handler(msg)
            async with self._commit_lock:
                if self.consumer:
                    assigned = await self.consumer.assignment()
                    if tp not in set(assigned):
                        logger.debug(f"Partition {tp} no longer assigned, skipping commit")
                        return
                    try:
                        await self.consumer.commit(
                            offsets=[TopicPartition(msg.topic(), msg.partition(), msg.offset() + 1)]
                        )
                    except Exception as e:
                        logger.warning(f"Offset commit failed: {e}")
        except asyncio.CancelledError:
            pass
        except Exception:
            tb = traceback.format_exc()
            logger.error(f"Error processing message: {msg.value().decode()}\n{tb}")
        finally:
            self._semaphore.release()

    async def _drain(self):
        """
        Internal task to pull messages from the queue and execute them using the semaphore.
        """
        while True:
            msg = await self._queue.get()
            if msg is None:
                break
            
            await self._semaphore.acquire()
            task = asyncio.create_task(self._handle_message(msg))
            self._live_tasks.add(task)
            task.add_done_callback(self._live_tasks.discard)

    async def start(self):
        """
        Starts the Kafka consumer loop and the background drain task.
        Includes automatic retry and connection recovery.
        """
        drain_task = asyncio.create_task(self._drain())
        retry_delay = 5

        while self.running:
            self.consumer = AIOConsumer(self.config)
            try:
                await self.consumer.subscribe([self.topic])
                logger.info(f"Subscribed to topic: {self.topic}")
                
                while self.running:
                    msg = await self.consumer.poll(timeout=1.0)
                    if msg is None:
                        continue
                    
                    if msg.error(): 
                        logger.error(f"Consumer error: {msg.error()}")
                        continue

                    # put_nowait keeps the poll loop non-blocking so librdkafka's
                    # heartbeat thread is never starved by handler processing.
                    self._queue.put_nowait(msg)
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception(f"Kafka consumer error — restarting in {retry_delay}s")
                # Clear the queue on error to avoid processing stale messages on reconnect
                while not self._queue.empty():
                    try:
                        self._queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
                await asyncio.sleep(retry_delay)
            finally:
                if self.consumer:
                    try:
                        await self.consumer.close()
                    except Exception:
                        pass
                logger.info("Consumer stopped.")

        # Signal the drain task to finish and wait for all processing to complete
        await self._queue.put(None)
        await drain_task
        
        # Ensure all currently running processing tasks are finished
        if self._live_tasks:
            await asyncio.gather(*self._live_tasks, return_exceptions=True)

    def stop(self):
        """
        Triggers a graceful shutdown of the worker.
        """
        self.running = False
