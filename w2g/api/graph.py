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


class Scope(core.Base):
    """A scope is an association between a directed edge and a context"""

    __tablename__ = 'edges_to_contexts'

    id = Column(BigInteger, primary_key=True)
    context_id = Column(BigInteger, ForeignKey('contexts.id'), nullable=False)
    edge_id = Column(BigInteger, ForeignKey('edges.id'), nullable=False)

    context = relationship('Context', backref='scopes')
    edge = relationship('Edge', backref='scopes')


class RemoteID(core.Base):
    """Associates an entity to its sources"""

    __tablename__ = "entities_to_sources"

    id = Column(BigInteger, primary_key=True)
    remote_id = Column(Unicode, nullable=False)
    entity_id = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    source_id = Column(BigInteger, ForeignKey('sources.id'), nullable=False)
    entity = relationship('Entity', backref='remote_ids')
    source = relationship('Source')


class Context(core.Base):
    """Contexts are named semantic groupings of directed edges which describe specific problem
    spaces or applications like math.mx or the-foundation.
    """

    __tablename__ = "contexts"

    id = Column(BigInteger, primary_key=True)
    entity_id = Column(BigInteger, ForeignKey('entities.id'))

    # A context's directed edges come from the edge id in its assocition through context_id
    entity = relationship('Entity', backref='contexts')

    def dict(self):        
        context = super(Context, self).dict()
        context['entity'] = self.entity.dict()
        return context


class Source(core.Base):
    """The remote service/source from which an entity tag has been sourced;
    e.g. facebook, google, stackoverflow, etc."""

    __tablename__ = "sources"

    id = Column(BigInteger, primary_key=True)
    entity_id = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    url = Column(Unicode, unique=True)  # see vendors.py
    entity = relationship('Entity')


class Edge(core.Base):
    """Directed edges between two entitites"""

    __tablename__ = "edges"

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

    id = Column(BigInteger, primary_key=True)
    name = Column(Unicode, nullable=False)

    # creator = Column(BigInteger, ForeignKey('users.id'))
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)
    modified = Column(DateTime(timezone=False), default=None)


class Metadata(core.Base):
    """An optimization to allow users to annotate remote entities with metadata,
    without making queries against entities slower"""

    __tablename__ = "metadata"

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
