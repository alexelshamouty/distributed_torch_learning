import json
import random

import oslo_messaging
from oslo_config import cfg
from scheduler.adapters.federated_learning import FederatedScheduler
from common.adapters.messaging_adapter import OsloMessaging
from database.adapters.sqlite import SqlLiteDatabase

CONF = cfg.CONF

scheduler_opts = [
    cfg.StrOpt(
        "rabbitmq_host", required=True, help="RabbitMQ server hostname for curator"
    ),
    cfg.StrOpt(
        "transport_url", required=True, help="RabbitMQ transport URL for curator"
    ),
    cfg.StrOpt("topic", required=True, help="RPC topic for curator"),
]
CONF.register_opts(scheduler_opts, group="scheduler")

CONF(default_config_files=["/app/ikaros.conf"])
WORKER_TOPIC_PREFIX = "worker-"

transport = oslo_messaging.get_rpc_transport(CONF, url=CONF.scheduler.transport_url)
target = oslo_messaging.Target(namespace="scheduler", version="1.0", topic=CONF.scheduler.topic, server="scheduler-service")


class SchedulerService:
    """Scheduler service listening for job requests and dispatching to workers."""
    def __init__(self):
        self.messaging = OsloMessaging(transport)
        self.database = SqlLiteDatabase()
        self.scheduler = FederatedScheduler(self.database, self.messaging)

    def schedule_job(self, context, job_data):
        task_spec = self.scheduler.schedule(context, job_data)
        self.scheduler.publish_task_scheduled(context, job_data, "node-1")
        return {"status": "scheduled", "node": "selected_node"}


def start_scheduler():
    """Starts the Oslo Messaging scheduler service."""
    endpoints = [SchedulerService()]
    server = oslo_messaging.get_rpc_server(transport, target, endpoints)

    print("Scheduler service started. Listening for jobs...")
    server.start()
    server.wait()


if __name__ == "__main__":
    start_scheduler()
