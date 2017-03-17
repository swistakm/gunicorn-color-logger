#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
import os


def get_version(version_tuple):
    if not isinstance(version_tuple[-1], int):
        return '.'.join(map(str, version_tuple[:-1])) + version_tuple[-1]
    return '.'.join(map(str, version_tuple))

try:
    from pypandoc import convert

    def read_md(f):
        return convert(f, 'rst')

except ImportError:
    convert = None
    print(
        "warning: pypandoc module not found, could not convert Markdown to RST"
    )

    def read_md(f):
        return open(f, 'r').read()  # noqa


init = os.path.join(os.path.dirname(__file__), 'gunicorn_color.py')
version_line = list(filter(lambda l: l.startswith('VERSION'), open(init)))[0]
VERSION = get_version(eval(version_line.split('=')[-1]))

INSTALL_REQUIRES = ['termcolor']
README = os.path.join(os.path.dirname(__file__), 'README.md')

setup(
    name='gunicorn_color',
    version=VERSION,

    description=(
        'Dead simple access logger for Gunicorn with termcolor support.'
    ),
    long_description=read_md(README),
    url='https://github.com/swistakm/gunicorn-color-logger',
    author='Michał Jaworski',
    author_email='swistakm@gmail.com',

    py_modules=['gunicorn_color'],
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    zip_safe=False,

    license='BSD',
    keywords='gunicorn, color, logger, logging',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

        'Topic :: Internet :: WWW/HTTP :: WSGI',
    ],
)
