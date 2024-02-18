import time
from typing import ClassVar, Any

from pydantic import BaseModel, Field


class Timer(BaseModel):
    template: str = "Elapsed time: {:0.4f} seconds"
    logger: Any = print
    start_time: None | float = None

    def __enter__(self):
        """Start a new timer as a context manager"""
        self.start()
        return self

    def __exit__(self, *exc_info):
        """Stop the context manager timer"""
        self.stop()

    def start(self):
        if self.start_time is not None:
            raise Exception("Timer is running. Use .stop() to stop it")

        self.start_time = time.perf_counter()

    def stop(self):
        if self.start_time is None:
            raise Exception("Timer is not running. Use .start() to run it")

        elapsed_time = time.perf_counter() - self.start_time
        self.start_time = None
        self.logger(self.template.format(elapsed_time))
