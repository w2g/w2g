#!/usr/bin/env python3
"""api init: SQLAlchemy engine + scoped session. DB from env (default sqlite)."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

DB_URI = os.environ.get("DATABASE_URL", "sqlite:///./data/w2g.db")
DEBUG = bool(int(os.environ.get("DEBUG", "0")))
engine = create_engine(
    DB_URI, echo=DEBUG,
    connect_args={"check_same_thread": False} if DB_URI.startswith("sqlite") else {},
)
db = scoped_session(sessionmaker(bind=engine))

from . import graph  # noqa: E402,F401  (registers models)
