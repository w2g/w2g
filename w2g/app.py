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
from api import core, db
from views import CustomJSONEncoder
from views import v1
import configs


current_version = v1
urls = ('/v1', v1,
        '', current_version
        )
app = router(Flask(__name__), urls)
app.secret_key = configs.SECRET_KEY
app.json_encoder = CustomJSONEncoder
cors = CORS(app) if configs.cors else None

if configs.DEBUG or configs.UWSGI:
    import sys
    if sys.version_info < (3, 0):
        from flask.ext.superadmin import Admin, model
        admin = Admin(app)
        for model in core.Base._decl_class_registry:
            try:
                admin.register(core.Base._decl_class_registry[model], session=db)
            except:
                pass

if __name__ == "__main__":
    app.run(**configs.options)
