import logging

import pytest
import structlog
from structlog.testing import capture_logs

from battle_python.logging_config import log_fn


def get_logger(log_level):
    structlog.reset_defaults()
    structlog.configure(
        processors=[structlog.processors.JSONRenderer()],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        cache_logger_on_first_use=False,
    )
    return structlog.get_logger()


@pytest.fixture()
def debug_logger():
    return get_logger(logging.DEBUG)


@pytest.fixture()
def info_logger():
    return get_logger(logging.INFO)


def test_log_fn_no_log_level(debug_logger):
    arg = "something"
    kwarg = {"keyword": "argument"}
    result = "some_result"

    @log_fn(logger=debug_logger)
    def foo(*args, **kwargs):
        return result

    # noinspection PyArgumentList
    with capture_logs() as cap_logs:
        foo(arg, **kwarg)

    assert {
        "args": f"'{arg}'",
        "event": "foo called",
        "log_level": "debug",
        **kwarg,
    } in cap_logs

    assert {
        "event": "foo returned",
        "log_level": "debug",
        "result": result,
    } in cap_logs


def test_log_fn_supplied_log_level(info_logger):
    arg = "something"
    kwarg = {"keyword": "argument"}
    result = "some_result"

    @log_fn(logger=info_logger, log_level="info")
    def foo(*args, **kwargs):
        return result

    # noinspection PyArgumentList
    with capture_logs() as cap_logs:
        foo(arg, **kwarg)

    assert {
        "args": f"'{arg}'",
        "event": "foo called",
        "log_level": "info",
        **kwarg,
    } in cap_logs

    assert {
        "event": "foo returned",
        "log_level": "info",
        "result": result,
    } in cap_logs


# TODO: See skip note. Fix this
@pytest.mark.skip(
    "I can't figure out how to properly configure log level filtering when testing"
)
def test_log_fn_not_logged(info_logger):
    arg = "something"
    kwarg = {"keyword": "argument"}
    result = "some_result"

    @log_fn(logger=info_logger, log_level="debug")
    def foo(*args, **kwargs):
        return result

    # noinspection PyArgumentList
    with capture_logs() as cap_logs:
        foo(arg, **kwarg)

    assert len(cap_logs) == 0


def test_log_fn_invalid_log_level(debug_logger):
    arg = "something"
    kwarg = {"keyword": "argument"}
    result = "some_result"

    with pytest.raises(ValueError) as e:
        # noinspection PyTypeChecker
        @log_fn(logger=debug_logger, log_level="DEBUG2")
        def foo(*args, **kwargs):
            return result

    assert "unhandled log_level" in str(e.value)


def test_log_fn_function_exception(debug_logger):
    arg = "something"
    kwarg = {"keyword": "argument"}
    result = "some_result"

    @log_fn(logger=debug_logger)
    def foo(*args, **kwargs):
        raise Exception("some exception")

    with pytest.raises(Exception) as e:
        # noinspection PyArgumentList
        with capture_logs() as cap_logs:
            foo(arg, **kwarg)

    assert "some exception" in str(e.value)
    assert {
        "args": f"'{arg}'",
        "event": "foo called",
        "log_level": "debug",
        **kwarg,
    } in cap_logs

    assert {
        "event": "Exception raised in foo. exception: some exception",
        "exc_info": True,
        "log_level": "error",
    } in cap_logs
