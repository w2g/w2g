#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    todo.py
    ~~~~~~~

    :copyright: (c) 2015 by Anonymous.
    :license: see LICENSE for more details.
"""

from flask import Flask
from flask.ext.routing import router
from flask.ext.cors import CORS
from views import CustomJSONEncoder
from views import v1
from configs import options, cors

current_version = v1
urls = ('/v1', v1,
        '', current_version
        )
app = router(Flask(__name__), urls)
app.json_encoder = CustomJSONEncoder
cors = CORS(app) if cors else None

if __name__ == "__main__":
    app.run(**options)
