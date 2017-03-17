[![Build Status](https://travis-ci.org/swistakm/gunicorn-color-logger.svg?branch=master)](https://travis-ci.org/swistakm/gunicorn-color-logger)
[![Coverage Status](https://coveralls.io/repos/github/swistakm/gunicorn-color-logger/badge.svg?branch=master)](https://coveralls.io/github/swistakm/gunicorn-color-logger?branch=master)

# Gunicorn color logger

Dead simple access logger for Gunicorn with termcolor support.

## Usage

Simply add `gunicorn_color` to your requirements file or install it manually:

    pip install gunicorn_color


Now you can use `gunicorn_color.Logger` as your gunicorn's logger class e.g.:

    gunicorn --access-logfile=- --logger-class=gunicorn_color.Logger wsgi::app [::]:8000


In order to disable colors **set** `ANSI_COLORS_DISABLED` environment variable:

    ANSI_COLORS_DISABLED= gunicorn --access-logfile=- --logger-class=gunicorn_color.Logger wsgi::app [::]:8000
