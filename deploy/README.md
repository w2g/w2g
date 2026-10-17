# Deploy w2g / graph.global on NEW (SQLite, FastAPI) — via the shared app pattern

Every converged app runs the same way: a venv + `uvicorn asgi:app` on a localhost port (from `.env`),
supervised by one shared systemd **template** unit. No per-app unit files.

## One-time on the server (install the template once)
```bash
sudo cp /srv/graph.global/deploy/app@.service /etc/systemd/system/   # shared by ALL apps
sudo systemctl daemon-reload
```

## Deploy this app
```bash
sudo mkdir -p /srv/graph.global && sudo chown $USER:$USER /srv/graph.global
git clone -b fastapi-port https://github.com/w2g/w2g.git /srv/graph.global
cd /srv/graph.global
cp .env.example .env          # set PORT=8092, DATABASE_URL, SECRET_KEY
mkdir -p data                 # scp the sqlite file in:
                              #   scp ~/Projects/linode/sqlite/w2g.db mek@NEW:/srv/graph.global/data/w2g.db
sudo systemctl enable --now app@graph.global      # run.sh builds the venv on first start
curl -s localhost:8092/v1/posts | head -c 120
```

## Update (idempotent)
```bash
cd /srv/graph.global && git pull
sudo systemctl restart app@graph.global
# only if requirements.txt changed:  rm -rf .venv  (run.sh rebuilds it) then restart
```

## Run manually (no systemd)
```bash
cd /srv/graph.global && bin/run.sh
```

TLS/vhost: `deploy/nginx-graph.global.conf` (proxy_pass -> 127.0.0.1:$PORT), cert via meksrv DNS-01.
Connect mek.fyi: flip graph.global DNS -> NEW (no mek.fyi change), or point mek.fyi GRAPH_POSTS at this app.
