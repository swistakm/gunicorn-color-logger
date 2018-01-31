[![Build Status](https://travis-ci.org/swistakm/gunicorn-color-logger.svg?branch=master)](https://travis-ci.org/swistakm/gunicorn-color-logger)
[![Coverage Status](https://coveralls.io/repos/github/swistakm/gunicorn-color-logger/badge.svg?branch=master)](https://coveralls.io/github/swistakm/gunicorn-color-logger?branch=master)

# Gunicorn color logger

Dead simple access logger for Gunicorn with termcolor support.

![screenshot](https://raw.githubusercontent.com/swistakm/gunicorn-color-logger/master/docs/screenshot.png)


## Usage - majority Python frameworks

Simply add `gunicorn_color` to your requirements file or install it manually:

    pip install gunicorn_color


Now you can use `gunicorn_color.Logger` as your gunicorn's logger class e.g.:

    gunicorn --access-logfile=- --logger-class=gunicorn_color.Logger wsgi::app [::]:8000


In order to disable colors **set** `ANSI_COLORS_DISABLED` environment variable:

    ANSI_COLORS_DISABLED= gunicorn --access-logfile=- --logger-class=gunicorn_color.Logger wsgi::app [::]:8000


## Usage - aiohttp

Gunicorn support in `aiohttp` library and configuration for access logs
in `aiohttp.GunicornWebWorker` are completely bonkers. Due to this you
need some extra effort in order to plug-in the `gunicorn_color` into
your application if it is based on aiohttp. Instead of using the
`--logger-class=gunicorn_color.Logger` you have to patch your
`aiohttp.web.Application()` directly using following code.

    # wsgi.py file with WSGI application object
    from functools import partial
    from gunicorn_color import AiohttpLogger
    from aiohttp import web

    app = web.Application()
    app.make_handler = partial(app.make_handler, access_log_class=AiohttpLogger)
