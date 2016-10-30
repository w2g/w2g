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


"""Used for naming/aliasing specific Edges with Entity"""
definitions = \
    Table('edges_to_entities', core.Base.metadata,
          Column('id', BigInteger, primary_key=True),
          Column('entity_id', BigInteger,
                 ForeignKey('entities.id'), nullable=False),
          Column('edge_id', BigInteger,
                 ForeignKey('edges.id'), nullable=False)
          )

"""The same Resource may be associated with `n` different entities"""
resource_entities = \
    Table('resources_to_entities', core.Base.metadata,
          Column('id', BigInteger, primary_key=True),
          Column('entity_id', BigInteger,
                 ForeignKey('entities.id'), nullable=False),
          Column('resource_id', BigInteger,
                 ForeignKey('resources.id'), nullable=False)
          )

"""The same Task may be associated with `n` different entities (keywords/tags)"""
task_entities = \
    Table('tasks_to_entities', core.Base.metadata,
          Column('id', BigInteger, primary_key=True),
          Column('entity_id', BigInteger,
                 ForeignKey('entities.id'), nullable=False),
          Column('resource_id', BigInteger,
                 ForeignKey('tasks.id'), nullable=False)
          )


"""Allows a checkin to attach resource bookmarks (placekeeping)"""
checkin_bookmarks = \
    Table('checkins_to_bookmarks', core.Base.metadata,
          Column('id', BigInteger, primary_key=True),
          Column('checkin_id', BigInteger,
                 ForeignKey('checkins.id'), nullable=False),
          Column('bookmark_id', BigInteger,
                 ForeignKey('bookmarks.id'), nullable=False)
          )

"""The same Resource may be associated with `n` edges"""
resource_edges = \
    Table('resources_to_edges', core.Base.metadata,
          Column('id', BigInteger, primary_key=True),
          Column('edge_id', BigInteger,
                 ForeignKey('edges.id'), nullable=False),
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
    """Contexts are a way to define discrete subsets of an Entity's
    Edges whose interpretation is unique to a specific domain or
    topic.

    As a data structure, a Context is a mapping between a semantic
    grouping of Edges and an Entity (a label / identifier).

    An Entity may either be viewed globally (context-free), or one may
    filter/retrieve a subset of the Entity's graph which includes only
    its Edges pertaining to a specific context. Many entities may
    implement/define the same Contexts (which may result in confusion
    if a Context itself has different interpretations, depending on
    the Edge's source).

    Contexts are a convenient way for people to create their own
    projects, applications, and domain sepcific taxonomies without
    forcing their Entity relations on a global level.
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

    def dict(self, verbose=False):
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
    names = relationship('Entity', secondary=definitions, backref="synonyms")
    # An edge's contexts come from the `edged` backref on Context

    resources = relationship('Resource', secondary=resource_edges,
                             backref="edges")

    def dict(self, verbose=False):
        edge = super(Edge, self).dict()
        edge['entities'] = [e.dict() for e in self.entity] \
            if self.entity else None
        if verbose:
            edge['source'] = self.source.dict()
            edge['target'] = self.target.dict()
            edge['relation'] = self.relation.dict()
            edge['resources'] = [r.dict() for r in self.resources]
            edge['contexts'] = [c.dict() for c in self.contexts]
            edge['names'] = [e.dict() for e in self.names]
        return edge


class Entity(core.Base):

    __tablename__ = "entities"

    id = Column(BigInteger, primary_key=True)
    name = Column(Unicode, nullable=False)

    relation_id = Column(BigInteger, ForeignKey('edges.id'), default=None)

    # creator = Column(BigInteger, ForeignKey('users.id'))
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)
    modified = Column(DateTime(timezone=False), default=None)
    avatar = Column(Unicode)
    data = Column(JSON)

    resources = relationship('Resource', secondary=resource_entities,
                             backref="tags")
    as_edge = relationship('Edge', primaryjoin="Entity.relation_id == Edge.id",
                           backref='entity')

    def dict(self, verbose=False):
        entity = super(Entity, self).dict()
        entity['remoteIds'] = [r.dict() for r in self.remote_ids]
        if verbose:
            entity['as_edge'] = self.as_edge.dict(verbose=True) if self.as_edge else None
            entity['edges'] = {
                'parents': [i.dict(verbose=True) for i in self.incoming_edges],
                'relations': [r.dict(verbose=True) for r in self.relations],
                'children': [o.dict(verbose=True) for o in self.outgoing_edges]
                }
            entity['resources'] = [r.dict() for r in self.resources]
        return entity


class Resource(core.Base):

    """XXX: Deprecate, just use entity + edge"""

    __tablename__ = "resources"

    id = Column(BigInteger, primary_key=True)
    url = Column(Unicode, unique=True)
    title = Column(Unicode)
    description = Column(Unicode)
    avatar = Column(Unicode)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)


class Bookmark(core.Base):
    """Keeps track of where you left off in a resource"""

    __tablename__ = "bookmarks"

    id = Column(BigInteger, primary_key=True)

    resource_id = Column(BigInteger, ForeignKey('resources.id'), nullable=False)
    # user_id = ... # a bookmark is associated with a user

    start_time = Column(DateTime(timezone=False), default=None)
    end_time = Column(DateTime(timezone=False), default=None)
    quantity = Column(Integer)  # Check in an amount of this entity
    start_pos = Column(Unicode)  # start (page? position? designated by css selector)
    end_pos = Column(Unicode)  # end (page? position? designated by css selector)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)
    resource = relationship('Resource', backref='checkins')


class Checkin(core.Base):
    """A checkin may attach zero or more bookmarks"""

    __tablename__ = "checkins"

    id = Column(BigInteger, primary_key=True)    
    task_id = Column(BigInteger, ForeignKey('tasks.id'), nullable=False)
    note = Column(Unicode)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)


class Task(core.Base):

    __tablename__ = "tasks"

    id = Column(BigInteger, primary_key=True)    
    title = Column(Unicode)
    start = Column(DateTime(timezone=False), default=None)
    end = Column(DateTime(timezone=False), default=None)
    created = Column(DateTime(timezone=False), default=datetime.utcnow,
                     nullable=False)
    

for model in core.Base._decl_class_registry:
    m = core.Base._decl_class_registry.get(model)
    try:
        core.models[m.__tablename__] = m
    except:
        pass
