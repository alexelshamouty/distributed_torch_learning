from oslo_versionedobjects import base
from oslo_versionedobjects import fields
from database.database import get_session
from database.models import Worker as DBWorker


class Worker(base.VersionedObjectDictCompat, base.VersionedObject):
    """Represents a worker (compute node) that can be managed remotely via RPC."""

    VERSION = "1.0"  # Object version for backward compatibility

    def __init__(self, context=None, **kwargs):
        super().__init__(**kwargs)
        self._context = context

    fields = {
        "id": fields.IntegerField(),
        "hostname": fields.StringField(),
        "vcpus": fields.IntegerField(),
        "gpus": fields.IntegerField(),
        "memory_mb": fields.IntegerField(),
        "disk_gb": fields.IntegerField(),
        "state": fields.StringField(),
        "last_seen": fields.DateTimeField(nullable=True),
    }

    @staticmethod
    def _from_db_object(context, worker, db_worker):
        """Converts a database row to a Worker object."""
        for field in worker.fields:
            setattr(worker, field, db_worker[field])
        worker._context = context
        return worker

    @base.remotable
    def create(self):
        """Creates a new worker in the database."""
        session = get_session()
        with session.begin():
            db_worker = DBWorker(
                hostname=self.hostname,
                vcpus=self.vcpus,
                gpus=self.gpus,
                memory_mb=self.memory_mb,
                disk_gb=self.disk_gb,
                state=self.state,
            )
            session.add(db_worker)
            session.flush()  # Ensures `id` is generated
            self._from_db_object(self._context, self, db_worker)

    @base.remotable
    def save(self):
        """Updates an existing worker in the database."""
        session = get_session()
        with session.begin():
            db_worker = session.query(DBWorker).filter_by(id=self.id).first()
            if not db_worker:
                raise Exception(f"Worker {self.id} not found")

            for field in self.fields:
                if field in db_worker.__dict__ and getattr(self, field) is not None:
                    setattr(db_worker, field, getattr(self, field))

            session.flush()

    @base.remotable_classmethod
    def get_by_id(cls, context, worker_id):
        """Retrieve a worker by its ID."""
        session = get_session()
        db_worker = session.query(DBWorker).filter_by(id=worker_id).first()
        if not db_worker:
            return None
        return cls._from_db_object(context, cls(), db_worker)

    @base.remotable_classmethod
    def get_by_hostname(cls, context, worker_hostname):
        """Retrieve a worker by its ID."""
        session = get_session()
        db_worker = session.query(DBWorker).filter_by(hostname=worker_hostname).first()
        if not db_worker:
            return None
        return cls._from_db_object(context, cls(), db_worker)

    @base.remotable_classmethod
    def list_all(cls, context):
        """Retrieve all workers."""
        session = get_session()
        db_workers = session.query(DBWorker).all()
        return [
            cls._from_db_object(context, cls(), db_worker) for db_worker in db_workers
        ]

    @base.remotable
    def delete(self):
        """Deletes a worker from the database."""
        session = get_session()
        with session.begin():
            db_worker = session.query(DBWorker).filter_by(id=self.id).first()
            if db_worker:
                session.delete(db_worker)
