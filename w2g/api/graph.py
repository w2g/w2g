#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    api/music.py
    ~~~~~~~~~~~~

    TodoDAV API

    :copyright: (c) 2015 by mek.
    :license: see LICENSE for more details.
"""

from random import randint
from datetime import datetime
from sqlalchemy import Column, Unicode, BigInteger, Integer, \
    Boolean, DateTime, ForeignKey, Table, exists, func
from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy.orm import relationship
from api import db, engine, core


def build_tables():
    """Builds database postgres schema"""
    MetaData().create_all(engine)


"""Associates a directed edge with a specific view"""
edges_to_views = \
    Table('edges_to_views', core.Base.metadata,
          Column('id', BigInteger, primary_key=True),
          Column('view_id', BigInteger,
                 ForeignKey('views.id'),
                 nullable=False),
          Column('edge_id', BigInteger,
                 ForeignKey('edges.id'),
                 nullable=False)
    )


class View(core.Base):
    """Views are named semantic groupings of directed edges which describe specific problem
    spaces or applications like math.mx or the-foundation.
    """

    __tablename__ = "views"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    name = Column(Unicode, unique=True, nullable=False)

    # A view's directed edges come from the edge id in its assocition through view_id
    edges = relationship('Edge', secondary=edges_to_views)


class Source(core.Base):
    """The remote service from which an entity tag has been sources,
    e.g. facebook, google, stackoverflow, etc."""

    __tablename__ = "sources"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    name = Column(Unicode, unique=True, nullable=False)


class Edge(core.Base):
    """Directed edges between two entitites"""

    __tablename__ = "edges"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    relation_eid = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    source_eid = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    target_eid = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)
    relation = relationship('Entity', foreign_keys=[relation_eid])
    source = relationship('Entity', foreign_keys=[source_eid])
    target = relationship('Entity', foreign_keys=[target_eid], backref="edges")


class Entity(core.Base):

    """Ask Jessy how to make things extend Entity"""
    __tablename__ = "entities"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    tag = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)
    service_id = Column(BigInteger, ForeignKey('sources.id'), nullable=False)
    # creator = Column(BigInteger, ForeignKey('users.id'))
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)
    modified = Column(DateTime(timezone=False), default=None)


class Metadata(core.Base):
    """An optimization to allow users to annotate remote entities with metadata,
    without making queries against entities slower"""

    __tablename__ = "metadata"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    entity_id = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    data = Column(JSON)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

for model in core.Base._decl_class_registry:
    m = core.Base._decl_class_registry.get(model)
    try:
        core.models[m.__tablename__] = m
    except:
        pass
