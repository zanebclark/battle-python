import functools
import json
from typing import Literal

import numpy as np
import numpy.typing as npt
import structlog
from logger_cloudwatch_structlog import setup_and_get_logger, AWSCloudWatchLogs
from pydantic import BaseModel
from structlog.typing import EventDict

log_levels = {"critical", "error", "warning", "info", "debug"}
LogLevel = Literal["critical", "error", "warning", "info", "debug"]


def get_aligned_masked_array(
    masked_array: npt.NDArray[np.int_], indexed_axes: bool = True
) -> str:
    rows, columns = masked_array.shape

    if indexed_axes:
        return "\n".join(
            [
                "".join([f"{row_num:>4}" for row_num in ["     |", *range(rows - 2)]]),
                "═" * (4 * rows),
                *[
                    "".join(
                        [
                            f"{rows - i - 3:>4} ║",
                            *[
                                f"{element:>4}"
                                for element in str(row)
                                .strip("[]")
                                .replace("'", "")
                                .split(" ")[1:-1]
                                if element != ""
                            ],
                        ]
                    )
                    for i, row in enumerate(masked_array[1:-1])
                ],
            ]
        )
    return "\n".join(
        [
            "".join(
                [
                    f"{element:>4}"
                    for element in str(row).strip("[]").replace("'", "").split(" ")
                    if element != ""
                ]
            )
            for row in masked_array
        ]
    )


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


def setup_and_get_logger_with_processors(log_level: str = "DEBUG"):
    processors = (
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.dict_tracebacks,
        structlog.processors.UnicodeDecoder(),
        structlog.threadlocal.merge_threadlocal,
        MyAWSCloudWatchLogs(
            callouts=["status_code", "event"], serializer=json.dumps, sort_keys=False
        ),
    )
    return setup_and_get_logger(processors=processors, level=log_level)


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
