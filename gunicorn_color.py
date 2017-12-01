"""Custom Gunicorn access logger with termcolor support."""

VERSION = (0, 1, 0)  # PEP 386  # noqa
__version__ = ".".join([str(x) for x in VERSION])  # noqa

import os
import sys
import traceback
from termcolor import colored

from gunicorn.glogging import Logger as GunicornBaseLogger

try:
    from aiohttp.helpers import AccessLogger as AiohttpBaseLogger
except ImportError:  # pragma: no cover
    AiohttpBaseLogger = None


__all__ = (
    "Logger",
    "AiohttpLogger",
)


def supports_color():  # pragma: no cover
    """Determine if stdout supports colors.

    **Note:** Taken from Django code base (django.core.mangament.color).
    See: https://github.com/django/django/blob/master/django/core/management/color.py
    """  # noqa
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (
        plat != 'win32' or 'ANSICON' in os.environ
    )

    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if not supported_platform or not is_a_tty:
        return False
    return True


class ColorLoggerMixin(object):
    """Mixin class that does common initialization and color handling."""

    CODE_COLOR_MAPPING = {
        '1': ('yellow',),
        '2': ('green',),
        '3': ('cyan',),
        '4': ('magenta',),
        '5': ('red',),
    }

    def __init__(self, *args, **kwargs):
        """Initialize logger and disable colors if not supported."""
        self._supports_color = supports_color()
        super(ColorLoggerMixin, self).__init__(*args, **kwargs)

    def colorize_msg(self, code, msg):
        """Colorize the message depending on HTTP return code category."""
        if self._supports_color:
            return colored(
                msg, *self.CODE_COLOR_MAPPING.setdefault(code[0], ())
            )
        else:
            return msg

    def colorize_atoms(self, atoms):
        """Colorize separate atoms.

        Depending on logger internals this method may modify atoms argument
        (in form of dict) in place or return new collection of atoms.
        """
        return atoms


class Logger(ColorLoggerMixin, GunicornBaseLogger):
    """Custom gunicorn logger with termcolor capabilities."""

    def access(self, resp, req, environ, request_time):
        """Write access log entry.

        **Note:** this is mostly a rewrite of the ``access()`` so we don't have
        to fiddle with ``self.access_log`` and parse raw messages format.

        We don't touch the access log format and it can be easily configured
        same way as the default ``gunicorn.glogging.Logger``.
        """
        if not (self.cfg.accesslog or self.cfg.logconfig or self.cfg.syslog):
            return

        atoms = self.atoms(resp, req, environ, request_time)

        # wrap atoms:
        # - make sure atoms will be tested properly
        # - if atom doesn't exist replace it by '-'
        safe_atoms = self.atoms_wrapper_class(atoms)
        safe_atoms = self.colorize_atoms(safe_atoms)
        try:
            msg = self.cfg.access_log_format % safe_atoms
            self.access_log.info(self.colorize_msg(atoms['s'], msg))
        except:
            self.error(traceback.format_exc())


if AiohttpBaseLogger is not None:
    class AiohttpLogger(ColorLoggerMixin, AiohttpBaseLogger):
        """Custom aiohttp access logger with termcolor capabilities."""

        def log(self, request, response, time):
            """Write access log entry to the logger.

            **Note:** this is mostly a rewrite of the ``log()`` so we
            don't have to fiddle with ``self.access_log`` and parse raw
            messages format. We don't touch the access log format and it can
            be easily configured same way as the default aiohttp logger.
            """
            try:
                fmt_info = self.colorize_atoms(
                    self._format_line(request, response, time)
                )

                values = list()
                extra = dict()
                for key, value in fmt_info:
                    values.append(value)

                    if key.__class__ is str:
                        extra[key] = value
                    else:
                        extra[key[0]] = {key[1]: value}

                self.logger.info(
                    self.colorize_msg(
                        str(response.status), self._log_format % tuple(values),
                    ),
                    extra=extra
                )

            except Exception:
                self.logger.exception("Error in logging")
