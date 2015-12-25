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


class Record(MethodView):
    @rest
    def get(self, cls, id):
        return graph.core.models[cls].get(id).dict()


class Page(MethodView):

    @rest
    @paginate(limit=50)
    def get(self, cls):
        if request.args.get('action') == 'search':
            return search(graph.core.models[cls])
        return graph.db.query(graph.core.models[cls])


    def post(self, cls):
        return request.form.keys()


class Database(MethodView):
    """Download a snapshot of the database"""
    pass


class Index(MethodView):
    @rest
    def get(self):
        # TODO: Query.execute ...
        return {"endpoints": graph.core.models.keys()}



urls = (
    '/<cls>/<int:id>', Record,
    '/<cls>', Page,
    '/db', Database,
    '/', Index # will become graphql endpoint
)
