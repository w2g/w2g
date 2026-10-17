# Deploy w2g / graph.global on NEW (SQLite-backed FastAPI)

This branch (`fastapi-port`) runs the w2g API on Python 3 + FastAPI + **SQLite** (no Postgres).
It reuses the original SQLAlchemy models (`w2g/api/*`); only the engine (env `DATABASE_URL`),
the JSON column import, BigInteger PK (sqlite autoincrement variant), and the SQLAlchemy-2.0
model registry were changed. The `/v1` REST API is reimplemented in `asgi.py`.

## Deploy
```bash
sudo mkdir -p /srv/graph.global && sudo chown $USER:$USER /srv/graph.global
git clone -b fastapi-port https://github.com/w2g/w2g.git /srv/graph.global
cd /srv/graph.global
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
# provision the data file out-of-band (from the mini):
#   scp ~/Projects/linode/sqlite/w2g.db mek@NEW:/srv/graph.global/data/w2g.db
mkdir -p data   # then drop w2g.db here
sudo cp deploy/w2g.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now w2g
curl -s localhost:8092/v1/posts | head -c 200     # expect JSON {"posts":[...]}
```
TLS/vhost: `deploy/nginx-graph.global.conf` (cert via the meksrv DNS-01 one-liner for graph.global).

## Connect mek.fyi
mek.fyi calls `GRAPH_POSTS` (default `https://graph.global/v1/posts`). Two options:
1. **Point graph.global DNS at NEW** (api.graph.global/graph.global A -> NEW) — mek.fyi needs no change.
2. **Override mek.fyi's upstream** to the local API: set its env/config to `http://127.0.0.1:8092/v1/posts`
   (mek.fyi's asgi.py reads GRAPH_POSTS from env once made configurable).

## Notes / TODO
- Reads are fully working (posts list, slug-search w/ related_posts, entity/edge lookups).
- Writes (POST/PUT) work for fresh schemas; the shipped w2g.db has BIGINT PKs (no sqlite autoincrement),
  so new-row creation needs explicit ids or a schema rebuilt from the models (BigIntPK variant).
- graph.global's static UI (w2g/static) is not wired up here; this serves the /v1 API.
