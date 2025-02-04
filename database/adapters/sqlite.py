from database.ports.database_ports import DatabasePort
from database.models import Base
from oslo_config import cfg
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

CONF = cfg.CONF
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the relative database path
DB_PATH = os.path.join(BASE_DIR, "oslo_db.sqlite")

# Define database configuration
db_opts = [
    cfg.StrOpt(
        "connection", default="sqlite:///" + DB_PATH, help="Database connection string"
    )
]
CONF.register_opts(db_opts, group="database")

# Create engine and session
_ENGINE = None
SessionLocal = None

class SqlLiteDatabase(DatabasePort):

    @staticmethod
    def get_engine(self):
        global _ENGINE
        if not _ENGINE:
            _ENGINE = create_engine(CONF.database.connection, echo=True)
        return _ENGINE
    
    @staticmethod
    def get_session(self):
        global SessionLocal
        if not SessionLocal:
            SessionLocal = sessionmaker(bind=self.get_engine())
        return SessionLocal()
    
    @staticmethod
    def init_db(self):
        """Initialize the database (used for testing)."""
        engine = self.get_engine()
        Base.metadata.create_all(engine)