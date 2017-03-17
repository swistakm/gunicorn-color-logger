try:
    from types import SimpleNamespace
except ImportError:
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
except ImportError:
    from mock import Mock

import pytest

import gunicorn_color
from gunicorn.config import Config


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
    monkeypatch.setattr(gunicorn_color, 'supports_color', lambda: True)
    monkeypatch.setenv('ANSI_COLORS_DISABLED', '')

    cfg = Config()
    cfg.set('accesslog', '-')

    logger = gunicorn_color.Logger(cfg)
    logger.access_log = Mock()

    logger.access(*access_args)

    msg = logger.access_log.info.call_args[0][0]

    assert not msg.startswith('\x1b[')
    assert not msg.endswith('\x1b[0m')
