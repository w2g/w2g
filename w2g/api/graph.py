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


"""Associates a directed edge with an entity"""
edge_entities = \
    Table('edges_to_entities', core.Base.metadata,
          Column('id', BigInteger, primary_key=True),
          Column('entity_id', BigInteger,
                 ForeignKey('entities.id'), nullable=False),
          Column('edge_id', BigInteger,
                 ForeignKey('edges.id'), nullable=False)
          )

class RemoteID(core.Base):
    """Associates an entity to its sources"""

    __tablename__ = "entities_to_sources"

    id = Column(BigInteger, primary_key=True)
    remote_id = Column(Unicode, nullable=False)
    entity_id = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    source_id = Column(BigInteger, ForeignKey('sources.id'), nullable=False)
    entity = relationship('Entity', backref='remote_ids')
    source = relationship('Source')


class Application(core.Base):
    """Applications are Entities which represent a semantic group
    of related edges. It associates directed edges to a specific
    topic, category, problem-space, or application like math.mx or the-foundation.
    """

    __tablename__ = "applications"

    id = Column(BigInteger, primary_key=True)
    entity_id = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    edge_id = Column(BigInteger, ForeignKey('edges.id'), nullable=False)

    entity = relationship('Entity')
    edge = relationship('Edge',
                        # All Applications of an edge can be retrieved
                        # by backref: edge.applications
                        backref='applications')

    def dict(self, verbose=False):
        app = super(Domain, self).dict()
        app['entity'] = self.entity.dict()
        if verbose:
            app['edges'] = [e.dict() for e in self.edges]
        return app


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
    source_eid = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    relation_eid = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    target_eid = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)

    # A source has this directed relation to this target.
    source = relationship('Entity', foreign_keys=[source_eid], backref='outgoing_edges')
    relation = relationship('Entity', foreign_keys=[relation_eid], backref='relations')
    target = relationship('Entity', foreign_keys=[target_eid], backref='incoming_edges')

    # This edge, the (source, relation, target) 3-tuple, can be
    # represented/described as the following entities
    representations = relationship('Entity', secondary=edge_entities, backref="synonyms")
    # An edge's applications come from the `edged` backref on Application

    def dict(self, verbose=False):
        edge = super(Edge, self).dict()
        if verbose:
            edge['source'] = self.source.dict()
            edge['target'] = self.target.dict()
            edge['entities'] = [e.dict() for e in self.entities]
            edge['applications'] = [a.dict() for a in self.applications]
        return edge


class Entity(core.Base):

    __tablename__ = "entities"

    id = Column(BigInteger, primary_key=True)
    name = Column(Unicode, nullable=False)

    # creator = Column(BigInteger, ForeignKey('users.id'))
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)
    modified = Column(DateTime(timezone=False), default=None)
    data = Column(JSON)

    def dict(self, verbose=False):
        entity = super(Entity, self).dict()
        entity['remoteIds'] = [r.dict() for r in self.remote_ids]
        if verbose:            
            entity['edges'] = {
                'parents': [i.dict(verbose=True) for i in self.incoming_edges],
                'children': [o.dict(verbose=True) for o in self.outgoing_edges]
                }
        return entity


for model in core.Base._decl_class_registry:
    m = core.Base._decl_class_registry.get(model)
    try:
        core.models[m.__tablename__] = m
    except:
        pass
