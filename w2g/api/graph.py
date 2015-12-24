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


"""Associates a directed edge with a specific context"""
edges_to_contexts = \
    Table('edges_to_contexts', core.Base.metadata,
          Column('id', BigInteger, primary_key=True),
          Column('context_id', BigInteger,
                 ForeignKey('contexts.id'),
                 nullable=False),
          Column('edge_id', BigInteger,
                 ForeignKey('edges.id'),
                 nullable=False)
    )

"""Associates an entity to its sources"""
entities_to_sources = \
    Table('entities_to_sources', core.Base.metadata,
          Column('id', BigInteger, primary_key=True),
          Column('entity_id', BigInteger,
                 ForeignKey('entities.id'),
                 nullable=False),
          Column('source_id', BigInteger,
                 ForeignKey('sources.id'),
                 nullable=False)
    )

class Context(core.Base):
    """Contexts are named semantic groupings of directed edges which describe specific problem
    spaces or applications like math.mx or the-foundation.
    """

    __tablename__ = "contexts"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    entity_id = Column(BigInteger, ForeignKey('entities.id'))

    # A context's directed edges come from the edge id in its assocition through context_id
    edges = relationship('Edge', secondary=edges_to_contexts)


class Source(core.Base):
    """The remote service/source from which an entity tag has been sourced;
    e.g. facebook, google, stackoverflow, etc."""

    __tablename__ = "sources"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    entity_id = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    url = Column(Unicode, unique=True)  # see vendors.py
    entity = relationship('Entity')


class Edge(core.Base):
    """Directed edges between two entitites"""

    __tablename__ = "edges"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    relation_eid = Column(BigInteger, ForeignKey('entities.id'))
    source_eid = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    target_eid = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)
    relation = relationship('Entity', foreign_keys=[relation_eid])
    source = relationship('Entity', foreign_keys=[source_eid])
    target = relationship('Entity', foreign_keys=[target_eid], backref="edges")


class Entity(core.Base):

    __tablename__ = "entities"
    TBL = __tablename__

    id = Column(BigInteger, primary_key=True)
    name = Column(Unicode, nullable=False)

    # creator = Column(BigInteger, ForeignKey('users.id'))
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)
    modified = Column(DateTime(timezone=False), default=None)
    sources = relationship('Source', secondary=entities_to_sources)


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
