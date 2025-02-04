from oslo_config import cfg
import oslo_messaging
import json
import random

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
target = oslo_messaging.Target(topic=CONF.scheduler.topic, server="scheduler-service")


class SchedulerService:
    """Scheduler service listening for job requests and dispatching to workers."""

    target = oslo_messaging.Target(namespace="scheduler", version="1.0")

    def schedule_job(self, context, job_data):
        """Selects a node and forwards the job to the corresponding worker queue."""
        available_nodes = ["node-1", "node-2", "node-3"]
        selected_node = random.choice(available_nodes)
        job_data["assigned_node"] = selected_node

        print(f"Scheduled job {job_data['job_id']} to {selected_node}")

        # Send the job to the selected worker topic
        worker_target = oslo_messaging.Target(
            topic=f"{WORKER_TOPIC_PREFIX}{selected_node}"
        )
        worker_client = oslo_messaging.RPCClient(transport, worker_target)
        worker_client.cast(context, "execute_job", job_data=job_data)
        return {"status": "scheduled", "node": selected_node}


def start_scheduler():
    """Starts the Oslo Messaging scheduler service."""
    endpoints = [SchedulerService()]
    server = oslo_messaging.get_rpc_server(transport, target, endpoints)

    print("Scheduler service started. Listening for jobs...")
    server.start()
    server.wait()


if __name__ == "__main__":
    start_scheduler()
