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
import graphene
from configs import DB_URI, DEBUG

engine = create_engine(DB_URI, echo=DEBUG, client_encoding='utf8')
db = scoped_session(sessionmaker(bind=engine))

from . import graph

# TODO: Move to graphql branch
class Query(graphene.ObjectType):
    pass

# Graphql code to go here. (register sqlalchemy endpoints)
#for k, v in core.Base._decl_class_registry.items():
#    setattr(Query, k, v)
#    setattr(Query, 'resolve_%s' % k, lambda
