import functools
import json
import logging
import platform
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal

import structlog
from logger_cloudwatch_structlog import AWSCloudWatchLogs
from pydantic import BaseModel
from structlog.typing import EventDict


log_levels = {"critical", "error", "warning", "info", "debug"}
LogLevel = Literal["critical", "error", "warning", "info", "debug"]
_NOISY_LOG_SOURCES = ("boto", "boto3", "botocore")


def get_log_file_path() -> Path:
    if platform.system() == "Windows":
        return Path(__file__).parent.parent.parent / "logs" / "log.log"
    log_file_path = Path("/var/log/battle-python/log.log")


class MyAWSCloudWatchLogs(AWSCloudWatchLogs):
    def __call__(self, _, name: str, event_dict: EventDict) -> str | bytes:
        """The return type of this depends on the return type of self._dumps."""

        header = f"[{name.upper()}] "
        callout_one = event_dict.get(self._callout_one_key, None)
        callout_two = event_dict.get(self._callout_two_key, None)

        if callout_one:
            header += f'"{callout_one}" '
        if callout_two:
            header += f'"{callout_two}" '

        try:
            return header + self._dumps(
                {
                    k: {str(sub_k): sub_v for sub_k, sub_v in v.items()}
                    if isinstance(v, dict)
                    else v
                    for k, v in event_dict.items()
                },
                **self._dumps_kw,
            )
        except TypeError:
            return header + self._dumps(str(event_dict), **self._dumps_kw)


def get_configured_logger(log_level: str = "DEBUG"):
    log_file_path = get_log_file_path()

    if not log_file_path.parent.is_dir():
        log_file_path.parent.mkdir(parents=True)

    processors = (
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.dict_tracebacks,
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
        structlog.threadlocal.merge_threadlocal,
        MyAWSCloudWatchLogs(
            callouts=["status_code", "event"], serializer=json.dumps, sort_keys=False
        ),
    )

    # This is from https://github.com/openlibraryenvironment/serverless-zoom-recordings
    # Structlog configuration
    structlog.configure(
        processors=processors,
        context_class=dict,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    file_handler = RotatingFileHandler(log_file_path, maxBytes=100000, backupCount=100)
    stream_handler = logging.StreamHandler(sys.stdout)

    logging.basicConfig(
        format="%(message)s",
        handlers=[file_handler, stream_handler],
        level=log_level,
        force=True,
    )
    for source in _NOISY_LOG_SOURCES:
        logging.getLogger(source).setLevel(logging.WARNING)
    return structlog.get_logger()


def log_fn(
    _func=None,
    *,
    logger: structlog.BoundLogger,
    log_level: LogLevel = "debug",
    log_args: bool = True,
):
    def generic_log_fn(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logged_kwargs = {
                k: v.model_dump() if isinstance(v, BaseModel) else v
                for k, v in kwargs.items()
            }
            if log_args:
                logged_kwargs["args"] = ", ".join([repr(arg) for arg in args])

            # noinspection PyProtectedMember
            logger._proxy_to_logger(
                log_level,
                f"{func.__name__} called",
                **logged_kwargs,
            )

            try:
                _result = func(*args, **kwargs)

                logged_result = _result
                if isinstance(_result, BaseModel):
                    logged_result = _result.model_dump()

                # noinspection PyProtectedMember
                logger._proxy_to_logger(
                    log_level, f"{func.__name__} returned", result=logged_result
                )
                return _result
            except Exception as e:
                logger.exception(
                    f"Exception raised in {func.__name__}. exception: {str(e)}"
                )
                raise e

        return wrapper

    if log_level not in log_levels:
        raise ValueError(
            f"unhandled log_level: {log_level}. Supported values: {', '.join(log_levels)}"
        )

    if _func is None:
        return generic_log_fn

    return generic_log_fn(_func)
