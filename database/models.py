from oslo_db.sqlalchemy import models
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Worker(Base, models.ModelBase):
    """Database model for workers."""

    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hostname = Column(String(255), nullable=False, unique=True)
    vcpus = Column(Integer, nullable=False, default=0)
    gpus = Column(Integer, nullable=False, default=0)
    memory_mb = Column(Integer, nullable=False, default=0)
    disk_gb = Column(Integer, nullable=False, default=0)
    state = Column(String(50), nullable=False, default="idle")  # e.g., idle, busy, down
    last_seen = Column(DateTime, default=datetime.utcnow, nullable=False)


class Job(Base, models.ModelBase):
    """Database model for jobs."""

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    github_url = Column(String(512), nullable=False)
    worker_name = Column(String(255), nullable=True)
    worker_id = Column(
        Integer, ForeignKey("workers.id"), nullable=True
    )  # References Worker.id
    status = Column(
        String(50), nullable=False, default="submitted"
    )  # e.g., submitted, running, completed
    submitted_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_update_date = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
