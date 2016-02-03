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


"""Used for naming edges: Associates a directed edge with an
entity. Challenge: How is this different than Context?"""
edge_entities = \
    Table('edges_to_entities', core.Base.metadata,
          Column('id', BigInteger, primary_key=True),
          Column('entity_id', BigInteger,
                 ForeignKey('entities.id'), nullable=False),
          Column('edge_id', BigInteger,
                 ForeignKey('edges.id'), nullable=False)
          )

"""The same Resource may be associated with `n` entities"""
resource_entities = \
    Table('resources_to_entities', core.Base.metadata,
          Column('id', BigInteger, primary_key=True),
          Column('entity_id', BigInteger,
                 ForeignKey('entities.id'), nullable=False),
          Column('resource_id', BigInteger,
                 ForeignKey('resources.id'), nullable=False)
          )


class RemoteId(core.Base):
    """Associates an entity to its sources"""

    __tablename__ = "entities_to_sources"

    id = Column(BigInteger, primary_key=True)
    remote_id = Column(Unicode, nullable=False)
    entity_id = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    source_id = Column(BigInteger, ForeignKey('sources.id'), nullable=False)
    entity = relationship('Entity', backref='remote_ids')
    source = relationship('Source')     


class Context(core.Base):
    """Contexts are Entities which represent a semantic group
    of related edges. It associates directed edges to a specific
    topic, category, problem-space, or application like math.mx or the-foundation.
    """

    __tablename__ = "contexts"

    id = Column(BigInteger, primary_key=True)
    entity_id = Column(BigInteger, ForeignKey('entities.id'), nullable=False)
    edge_id = Column(BigInteger, ForeignKey('edges.id'), nullable=False)

    entity = relationship('Entity')
    edge = relationship('Edge',
                        # All Contexts of an edge can be retrieved
                        # by backref: edge.contexts
                        backref='contexts')

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

    def dict(self):
        source = super(Source, self).dict()
        source['entity'] = self.entity.dict()
        return source


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
    names = relationship('Entity', secondary=edge_entities, backref="synonyms")
    # An edge's contexts come from the `edged` backref on Context

    def dict(self, verbose=False):
        edge = super(Edge, self).dict()
        if verbose:
            edge['source'] = self.source.dict()
            edge['target'] = self.target.dict()
            edge['entities'] = [e.dict() for e in self.entities]
            edge['contexts'] = [c.dict() for c in self.contexts]
        return edge


class Entity(core.Base):

    __tablename__ = "entities"

    id = Column(BigInteger, primary_key=True)
    name = Column(Unicode, nullable=False)

    # creator = Column(BigInteger, ForeignKey('users.id'))
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)
    modified = Column(DateTime(timezone=False), default=None)
    avatar = Column(Unicode)
    data = Column(JSON)
    
    resources = relationship('Resource', secondary=resource_entities,
                             backref="entities")

    def dict(self, verbose=False):
        entity = super(Entity, self).dict()
        entity['remoteIds'] = [r.dict() for r in self.remote_ids]
        if verbose:            
            children = self.outgoing_edges
            entity['edges'] = {
                'parents': [i.dict(verbose=True) for i in self.incoming_edges],
                'children': [o.dict(verbose=True) for o in children]
                }
            entity['resources'] = [r.dict() for r in self.resources]
            #entity['contexts'] = [c.dict() for c in children.contexts]
        return entity


class Resource(core.Base):

    __tablename__ = "resources"

    id = Column(BigInteger, primary_key=True)
    url = Column(Unicode, unique=True)
    title = Column(Unicode)
    description = Column(Unicode)
    avatar = Column(Unicode)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)


class Checkin(core.Base):

    __tablename__ = "checkins"

    id = Column(BigInteger, primary_key=True)
    resource_id = Column(BigInteger, ForeignKey('resources.id'), nullable=False)
    # activity_id = Column(BigInteger, ForeignKey('activities.id'), nullable=False)
    start_time = Column(DateTime(timezone=False), default=None)
    end_time = Column(DateTime(timezone=False), default=None)
    quantity = Column(Integer)  # Check in an amount of this entity
    start_pos = Column(Unicode)  # start (page? position? designated by css selector)
    end_pos = Column(Unicode)  # end (page? position? designated by css selector)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)
    resource = relationship('Resource', backref='checkins')



for model in core.Base._decl_class_registry:
    m = core.Base._decl_class_registry.get(model)
    try:
        core.models[m.__tablename__] = m
    except:
        pass
