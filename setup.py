#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    setup.py
    ~~~~~~~~

    w2g World Wide Graph

    :copyright: (c) 2015 by mek.
    :license: see LICENSE for more details.
"""

import codecs
import os
import re
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """Taken from pypa pip setup.py:
    intentionally *not* adding an encoding option to open, See:
       https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    """
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='w2g',
    version=find_version("w2g", "__init__.py"),
    description='no description available',
    long_description=read('README.md'),
    classifiers=[
        ],
    author='mek',
    author_email='',
    url='',
    packages=[
        'w2g'
        ],
    platforms='any',
    license='LICENSE',
    install_requires=[
        'Flask >= 0.10.1',
        'Flask-Routing',
        'Flask-SuperAdmin',
        'flask-cors',
        'psycopg2 >= 2.7.5',
        'requests >= 1.2.3',
        'sqlalchemy >= 1.0.6',
        'graphene'
        ]
)
