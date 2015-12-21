#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    api/__init__.py
    ~~~~~~~~~~~~~~~

    Initialization & DB Connections for the Groovebox APIs

    :copyright: (c) 2015 by mek.
    :license: see LICENSE for more details.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from configs import DB_URI, DEBUG

engine = create_engine(DB_URI, echo=DEBUG, client_encoding='utf8')
db = scoped_session(sessionmaker(bind=engine))

