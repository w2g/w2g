#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    __init__.py
    ~~~~~~~~~~~

    Common utilities for views

    :copyright: (c) 2015 by Mek.
    :license: see LICENSE for more details.
"""

from flask import jsonify, request
from flask import Flask, jsonify
from flask.json import JSONEncoder
import calendar
from datetime import datetime


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                if obj.utcoffset() is not None:
                    obj = obj - obj.utcoffset()
                    millis = int(
                        calendar.timegm(obj.timetuple()) * 1000 +
                        obj.microsecond / 1000
                    )
                    return millis
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


def rest(f):
    def inner(*args, **kwargs):
        try:
            return jsonify(f(*args, **kwargs))
        except Exception as e:
            return jsonify({"error": str(e)})
    return inner


def paginate(limit=100, dump=lambda i, **opts: i.dict(**opts), **options):
    """Decorator for returning paginated json data"""
    def outer(f):
        def inner(self, cls, *args, **kwargs):
            _limit = min(request.args.get("limit", limit), limit)
            _offset = request.args.get("page", 0) * _limit
            query = f(self, cls, *args, **kwargs)
            items = query.limit(_limit).offset(_offset).all()
            # consider returning total obj count and/or current limit + page
            return {cls: [dump(i, **options) for i in items]}
        return inner
    return outer
