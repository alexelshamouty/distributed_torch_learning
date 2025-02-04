from oslo_versionedobjects import base, fields

from database import get_session
from database.models import Job as DBJob


class Task(base.VersionedObjectDictCompat, base.PersistentObject, base.VersionedObject):
    """Represents a task (job) object for database interactions."""

    VERSION = "1.0"  # Versioning for backward compatibility

    fields = {
        "id": fields.IntegerField(),
        "name": fields.StringField(),
        "github_url": fields.StringField(),
        "worker_name": fields.StringField(nullable=True),
        "worker_id": fields.IntegerField(nullable=True),
        "status": fields.StringField(),
        "submitted_date": fields.DateTimeField(nullable=True),
        "last_update_date": fields.DateTimeField(nullable=True),
    }

    @staticmethod
    def _from_db_object(context, task, db_task):
        """Converts a database row to a Task object."""
        for field in task.fields:
            setattr(task, field, db_task[field])
        task._context = context
        return task

    @base.remotable
    def create(self):
        """Creates a new job in the database."""
        session = get_session()
        with session.begin():
            db_task = DBJob(
                name=self.name,
                github_url=self.github_url,
                worker_name=self.worker_name,
                worker_id=self.worker_id,
                status=self.status,
            )
            session.add(db_task)
            session.flush()  # Ensures `id` is generated
            self._from_db_object(self._context, self, db_task)

    @base.remotable
    def save(self):
        """Updates an existing job in the database."""
        session = get_session()
        with session.begin():
            db_task = session.query(DBJob).filter_by(id=self.id).first()
            if not db_task:
                raise Exception(f"Job {self.id} not found")

            for field in self.fields:
                if field in db_task.__dict__ and getattr(self, field) is not None:
                    setattr(db_task, field, getattr(self, field))

            session.flush()

    @base.remotable_classmethod
    def get_by_id(cls, context, job_id):
        """Retrieve a job by its ID."""
        session = get_session()
        db_task = session.query(DBJob).filter_by(id=job_id).first()
        if not db_task:
            return None
        return cls._from_db_object(context, cls(), db_task)

    @base.remotable_classmethod
    def list_all(cls, context):
        """Retrieve all jobs."""
        session = get_session()
        db_tasks = session.query(DBJob).all()
        return [cls._from_db_object(context, cls(), db_task) for db_task in db_tasks]

    @base.remotable
    def delete(self):
        """Deletes a job from the database."""
        session = get_session()
        with session.begin():
            db_task = session.query(DBJob).filter_by(id=self.id).first()
            if db_task:
                session.delete(db_task)
