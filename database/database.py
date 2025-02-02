from oslo_config import cfg
from oslo_db.sqlalchemy import session as db_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

CONF = cfg.CONF

# Define database configuration
db_opts = [
    cfg.StrOpt('connection', default='sqlite:///oslo_db.sqlite', help='Database connection string')
]
CONF.register_opts(db_opts, group='database')

# Create engine and session
_ENGINE = None
SessionLocal = None

def get_engine():
    global _ENGINE
    if not _ENGINE:
        _ENGINE = create_engine(CONF.database.connection, echo=True)
    return _ENGINE

def get_session():
    global SessionLocal
    if not SessionLocal:
        SessionLocal = sessionmaker(bind=get_engine())
    return SessionLocal()

def init_db():
    """Initialize the database (used for testing)."""
    engine = get_engine()
    Base.metadata.create_all(engine)
