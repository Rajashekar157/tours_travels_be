from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from psycopg2.pool import ThreadedConnectionPool
from dotenv import load_dotenv
import os
import logging

# -------------------------------------------------
# LOAD ENV
# -------------------------------------------------
load_dotenv()

# -------------------------------------------------
# LOGGING
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("database")

# -------------------------------------------------
# SQLALCHEMY CONFIG
# -------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL not set")

# Use Render DATABASE_URL (postgresql+psycopg2://...)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # avoids stale connections
    pool_size=5,
    max_overflow=10,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    """Dependency for FastAPI routes to get a DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------------------------
# PSYCOPG2 RAW CONNECTION POOL (OPTIONAL)
# -------------------------------------------------
PSYCOPG2_DSN = os.getenv("PSYCOPG2_DSN")

db_pool: ThreadedConnectionPool | None = None

if PSYCOPG2_DSN:
    try:
        db_pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=PSYCOPG2_DSN
        )
        logger.info("✅ psycopg2 ThreadedConnectionPool connected")
    except Exception as e:
        logger.error("❌ psycopg2 pool connection failed: %s", e)
        db_pool = None
else:
    logger.warning("⚠️ PSYCOPG2_DSN not set — raw DB disabled")

def get_raw_conn():
    """
    Generator for raw psycopg2 connections.
    Use only when needed (bulk ops, raw SQL).
    """
    if not db_pool:
        raise RuntimeError("Raw DB connection not available")

    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)
