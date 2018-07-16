#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    endpoints.py
    ~~~~~~~~~~~~

    :copyright: (c) 2015 by Anonymous.
    :license: see LICENSE for more details.
"""

from flask import request, Response
from flask.views import MethodView
from api import graph  # Query 
from views import paginate, rest, search

# Issue: Move limit out of @paginate and into get(self, limit=...) so
# other methods (like search) can use it.

"""

If I hit /foo I want a list of all edges for a Collection
"""


class Record(MethodView):
    @rest
    def get(self, cls, id):        
        return graph.core.models[cls].get(id).dict(verbose=True)

    @rest
    def put(self, cls, id):
        c = graph.core.models[cls].get(id)
        for k, v in request.form.items():
            setattr(c, k, v)
        c.save()
        return c.dict(verbose=True)


class Page(MethodView):

    @rest
    @paginate(limit=50)
    def get(self, cls):
        if request.args.get('action') == 'search':
            return search(graph.core.models[cls])
        if request.args.get('action') == 'leaderboard':
            return graph.core.models[cls].leaderboard(limit=10)
        return graph.db.query(graph.core.models[cls])

    @rest
    def post(self, cls):        
        c = graph.core.models[cls](**dict([(i, j) for i, j in request.form.items()]))
        c.create()
        return c.dict()


class EntityResources(MethodView):

    @rest
    def get(self, id):
        e = graph.Entity.get(id)
        return {'resources': [r.dict() for r in e.resources]}


    @rest
    def post(self, id):
        e = graph.Entity.get(id)
        e.resources.append(graph.Resource.get(request.form.get('resource_id')))
        e.save()
        return e.dict()                           


class EntityDelete(MethodView):

    @rest
    def get(self, id):
        e = graph.Entity.get(id)
        e.remove()

class EntityEdges(MethodView):

    @rest
    def get(self, id=None):
        e = graph.Entity.get(id)
        return {'edges': e.dict(verbose=True)['edges']}

    @rest
    def post(self, id):
        source = graph.Entity.get(id)
        relation_eid = request.form.get('relation_eid')
        target_eid = request.form.get('target_eid')
        e = graph.Edge(
            source_eid=source.id,
            relation_eid=relation_eid,
            target_eid=target_eid
            )
        e.create()
        return e.dict()


class Edge(MethodView):

    @rest
    def get(self, id=None):
        e = graph.Edge.get(id)
        return e.dict()


class EdgeDelete(MethodView):

    @rest
    def get(self, id=None):
        e = graph.Edge.get(id)
        return e.remove()


class Database(MethodView):
    """Download a snapshot of the database"""
    pass


class Index(MethodView):
    @rest
    def get(self):
        # TODO: Query.execute ...
        return {"endpoints": graph.core.models.keys()}


class Merge(MethodView):
    @rest
    def get(self, a, b):
        e1 = graph.Entity.get(a)
        e2 = graph.Entity.get(b)
        # Preserve data
        r = graph.RemoteId(entity_id=e1.id)
        graph.db.expunge(r)
        graph.db.expunge(e1)
        graph.db.commit()


urls = (
    '/merge/<int:a>/<int:b>', Merge,
    '/entities/<int:id>/resources', EntityResources,
    '/edges/<int:id>/delete', EdgeDelete,
    '/edges/<int:id>', Edge,
    '/entities/<int:id>/edges', EntityEdges,
    '/entities/<int:id>/delete', EntityDelete,
    '/<cls>/<int:id>', Record,
    '/<cls>', Page,
    '/db', Database,
    '/', Index # will become graphql endpoint
)
