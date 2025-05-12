"""
The Background Common module.

Defines primitives for executing I/O blocking operations in the background using
a thread pool executor.
"""

import asyncio
from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor


###
# Thread pool executor used strictly to perform blocking operations in background
###

MAX_THREAD_POOL_SIZE = 100

BACKGROUND_THREAD_POOL_EXECUTOR = ThreadPoolExecutor(
    max_workers=MAX_THREAD_POOL_SIZE, thread_name_prefix="background_worker_"
)


async def run_async(func: Callable[..., Any], *args, **kwargs) -> Any:
    """
    Runs a callable on the background thread pool executor using the current thread's
      I/O loop instance.

    Usage:
        def blocking_task(arg1, arg2, arg3):
            # ...
            # does some blocking stuff
            # ...

        run_async(blocking_task, arg1, arg2, arg3)

    :param Callable[..., Any] func: the function or callable to run in background
    :param tuple args: function arguments
    :param dict kwargs: function named arguments
    :return: funcs return value
    """

    def work():
        return func(*args, **kwargs)

    return await asyncio.get_event_loop().run_in_executor(
        BACKGROUND_THREAD_POOL_EXECUTOR, work
    )


tasks = set()


def run_fire_forget(func: Callable[..., Any], *args, **kwargs) -> None:
    future = asyncio.ensure_future(run_async(func, *args, **kwargs))

    tasks.add(future)

    future.add_done_callback(lambda _: tasks.remove(future))
