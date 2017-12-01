import time
import sys

try:
    from types import SimpleNamespace
except ImportError:  # pragma: no cover
    class SimpleNamespace(object):
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

        def __repr__(self):
            keys = sorted(self.__dict__)
            items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
            return "{}({})".format(type(self).__name__, ", ".join(items))

        def __eq__(self, other):
            return self.__dict__ == other.__dict__

try:
    from unittest.mock import Mock
except ImportError:  # pragma: no cover
    from mock import Mock

import pytest

try:
    from aiohttp.web import Response as AiohttpResponse
    from aiohttp.test_utils import (
        make_mocked_request as make_aiohttp_request_mock
    )
except ImportError:
    pass

from gunicorn.config import Config

import gunicorn_color


aiohttp_optional = pytest.mark.skipif(
    sys.version_info < (3, 4),
    reason="aiohttp does not support Python < 3.5"
)


@pytest.fixture
def access_args():
    response = SimpleNamespace(
        status='200', response_length=1024,
        headers=(('Content-Type', 'application/json'),), sent=1024,
    )
    request = SimpleNamespace(headers=(('Accept', 'application/json'),))
    environ = {
        'REQUEST_METHOD': 'GET', 'RAW_URI': '/my/path?foo=bar',
        'PATH_INFO': '/my/path', 'QUERY_STRING': 'foo=bar',
        'SERVER_PROTOCOL': 'HTTP/1.1',
    }

    request_time = SimpleNamespace(seconds=1, microseconds=2)
    return response, request, environ, request_time


def test_with_color(access_args, monkeypatch):
    monkeypatch.setattr(gunicorn_color, 'supports_color', lambda: True)

    cfg = Config()
    cfg.set('accesslog', '-')

    logger = gunicorn_color.Logger(cfg)
    logger.access_log = Mock()

    logger.access(*access_args)

    msg = logger.access_log.info.call_args[0][0]

    assert msg.startswith('\x1b[')
    assert msg.endswith('\x1b[0m')


def test_without_color(access_args, monkeypatch):
    monkeypatch.setattr(gunicorn_color, 'supports_color', lambda: False)
    monkeypatch.setenv('ANSI_COLORS_DISABLED', '')

    cfg = Config()
    cfg.set('accesslog', '-')

    logger = gunicorn_color.Logger(cfg)
    logger.access_log = Mock()

    logger.access(*access_args)

    msg = logger.access_log.info.call_args[0][0]

    assert not msg.startswith('\x1b[')
    assert not msg.endswith('\x1b[0m')


@aiohttp_optional
def test_aiohttp_with_color(monkeypatch):
    monkeypatch.setattr(gunicorn_color, 'supports_color', lambda: True)

    request = make_aiohttp_request_mock('GET', '/', headers={'token': 'x'})
    response = AiohttpResponse()

    mock_logger = Mock()

    logger = gunicorn_color.AiohttpLogger(mock_logger)
    logger.log(request, response, time.time())

    assert mock_logger.info.called
    # this is the last msg passed to logger through info
    msg = mock_logger.info.call_args[0][0]
    assert msg.startswith('\x1b[')
    assert msg.endswith('\x1b[0m')


@aiohttp_optional
def test_aiohttp_without_color(monkeypatch):
    monkeypatch.setattr(gunicorn_color, 'supports_color', lambda: False)

    request = make_aiohttp_request_mock('GET', '/', headers={'token': 'x'})
    response = AiohttpResponse()

    mock_logger = Mock()

    logger = gunicorn_color.AiohttpLogger(mock_logger)
    logger.log(request, response, time.time())

    assert mock_logger.info.called
    # this is the last msg passed to logger through info
    msg = mock_logger.info.call_args[0][0]
    assert not msg.startswith('\x1b[')
    assert not msg.endswith('\x1b[0m')
