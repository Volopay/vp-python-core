import time
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any, TypeVar

from vp_core.logging.logger import setup_logger

logger = setup_logger()

T = TypeVar("T")


def _format_args(args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    formatted_args: list[str] = []
    for arg in args:
        if isinstance(arg, str) and len(arg) > 200:
            formatted_args.append(f"str(len={len(arg)})")
        else:
            formatted_args.append(repr(arg))

    formatted_kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, str) and len(value) > 200:
            formatted_kwargs[key] = f"str(len={len(value)})"
        else:
            formatted_kwargs[key] = repr(value)

    return f"args={formatted_args}, kwargs={formatted_kwargs}"


def async_timed() -> (
    Callable[
        [Callable[..., Coroutine[Any, Any, T]]], Callable[..., Coroutine[Any, Any, T]]
    ]
):
    def wrapper(
        func: Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapped(*args: Any, **kwargs: Any) -> T:
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            formatted_args = _format_args(args, kwargs)
            logger.info(
                f"BENCHMARK: {func.__name__} took {end_time - start_time:.2f}s "
                f"with {formatted_args}"
            )
            return result

        return wrapped

    return wrapper


def timed() -> Callable[[Callable[..., T]], Callable[..., T]]:
    def wrapper(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> T:
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            formatted_args = _format_args(args, kwargs)
            logger.info(
                f"""BENCHMARK: {func.__name__} with {formatted_args}
                    took {end_time - start_time:.2f} seconds"""
            )
            return result

        return wrapped

    return wrapper
