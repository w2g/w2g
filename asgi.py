#!/usr/bin/env python3
"""
FastAPI (py3) port of the w2g / graph.global API, backed by SQLite.
Reuses the SQLAlchemy models in w2g/api/* and reimplements the /v1 REST layer.
Consumed by mek.fyi (/v1/posts) and w2g.js (entity lookups).
Run:  uvicorn asgi:app   (DATABASE_URL defaults to sqlite:///./data/w2g.db)
"""
import os, re, sys
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "w2g"))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from api import db, graph
core = graph.core

app = FastAPI(title="w2g / graph.global")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"], allow_credentials=True)

def enc(o):
    if isinstance(o, datetime): return o.strftime("%a, %d %b %Y %H:%M:%S GMT")
    if isinstance(o, dict):     return {k: enc(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [enc(x) for x in o]
    return o

def respond(fn):
    try:
        return JSONResponse(enc(fn()))
    except Exception as e:
        return JSONResponse({"error": str(e)})
    finally:
        db.rollback(); db.remove()

def M(cls): return core.models[cls]

@app.get("/v1")
@app.get("/v1/")
def index(): return respond(lambda: {"endpoints": list(core.models.keys())})

@app.get("/v1/entities/{id}/resources")
def entity_resources(id: int):
    return respond(lambda: {"resources": [r.dict() for r in graph.Entity.get(id).resources]})

@app.get("/v1/entities/{id}/edges")
def entity_edges(id: int):
    return respond(lambda: {"edges": graph.Entity.get(id).dict(verbose=True)["edges"]})

@app.get("/v1/edges/{id}")
def edge_get(id: int):
    return respond(lambda: graph.Edge.get(id).dict())

@app.get("/v1/{cls}/{id}")
def record_get(cls: str, id: int):
    return respond(lambda: M(cls).get(id).dict(verbose=True))

@app.get("/v1/{cls}")
def page_get(cls: str, request: Request):
    q = request.query_params
    def f():
        limit = min(int(q.get("limit", 50)), 50)
        page = int(q.get("page", 0))
        verbose = bool(int(q.get("verbose", 0)))
        m = M(cls)
        if q.get("action") == "search":
            items = m.search(q.get("query"), field=q.get("field"), limit=limit, lazy=True).all()
        elif q.get("action") == "leaderboard":
            items = list(m.leaderboard())
        else:
            items = db.query(m).limit(limit).offset(page * limit).all()
        return {cls: [i.dict(verbose=verbose) for i in items]}
    return respond(f)

@app.post("/v1/{cls}")
async def page_post(cls: str, request: Request):
    form = dict(await request.form())
    def f():
        c = M(cls)(**form); c.create()
        if cls == "posts":
            for tid in re.findall(r'\[\[([0-9]+):', form.get("title", "") + form.get("post", "")):
                try: c.tags.append(graph.Entity.get(tid))
                except Exception: pass
            c.save()
        return c.dict()
    return respond(f)

@app.put("/v1/{cls}/{id}")
async def record_put(cls: str, id: int, request: Request):
    form = dict(await request.form())
    def f():
        c = M(cls).get(id)
        for k, v in form.items(): setattr(c, k, v)
        c.save()
        return c.dict(verbose=True)
    return respond(f)

@app.get("/")
def health(): return respond(lambda: {"ok": True, "endpoints": list(core.models.keys())})
