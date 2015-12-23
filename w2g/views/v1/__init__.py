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
from views import paginate, rest


class Record(MethodView):
    @rest
    def get(self, cls, id):
        return graph.core.models[cls].get(id).dict()


class Page(MethodView):

    @rest
    @paginate(limit=50)
    def get(self, cls):
        return graph.db.query(graph.core.models[cls])


    def post(self, cls):
        return request.form.keys()


class Index(MethodView):
    @rest
    def get(self):
        # TODO: Query.execute ...
        return {"endpoints": graph.core.models.keys()}



urls = (
    '/<cls>/<int:id>', Record,
    '/<cls>', Page,
    '/', Index # will become graphql endpoint
)
