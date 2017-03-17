"""Custom Gunicorn access logger with termcolor support."""

VERSION = (0, 0, 1)  # PEP 386  # noqa
__version__ = ".".join([str(x) for x in VERSION])  # noqa

import os
import sys
import traceback
from termcolor import colored

from gunicorn.glogging import Logger as GunicornLogger


def supports_color():
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


class Logger(GunicornLogger):
    """Custom gunicorn logger with termcolor capabilities."""

    #: Mapping of code category to :func:`termcolor.colored()` function
    #: positional arguments. Replace dict in order to modify the coloring.
    CODE_COLOR_MAPPING = {
        '1': ('yellow', ),
        '2': ('green', ),
        '3': ('cyan', ),
        '4': ('magenta', ),
        '5': ('red', ),
    }

    def __init__(self, cfg):
        """Initialize logger and disable colors if not supported."""
        super(Logger, self).__init__(cfg)

        if not supports_color():
            self.colorize_msg = lambda code, msg: msg
            self.colorize_atoms = lambda atoms: atoms

    def colorize_msg(self, code, msg):
        """Colorize the message depending on HTTP return code category."""
        return colored(msg, *self.CODE_COLOR_MAPPING.setdefault(code[0], ()))

    def colorize_atoms(self, atoms):
        """Colorize separate atoms.

        This method is only stub for custom user-based extensions. It should
        modify ``atoms`` dict in situ. Note that it will interfere with the
        ``colorize_msg`` method that should be disabled if you want to colorize
        separate atoms of the access log.
        """

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
        # - make sure atoms will be test case insensitively
        # - if atom doesn't exist replace it by '-'
        safe_atoms = self.atoms_wrapper_class(atoms)
        self.colorize_atoms(safe_atoms)
        try:
            msg = self.cfg.access_log_format % safe_atoms
            self.access_log.info(self.colorize_msg(atoms['s'], msg))
        except:
            self.error(traceback.format_exc())
