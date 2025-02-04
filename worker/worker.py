from oslo_config import cfg
import oslo_messaging
import time
import socket

# Define configuration options
CONF = cfg.CONF

compute_opts = [
    cfg.StrOpt(
        "rabbitmq_host", required=True, help="RabbitMQ server hostname for compute"
    ),
    cfg.StrOpt(
        "transport_url", required=True, help="RabbitMQ transport URL for compute"
    ),
    cfg.StrOpt("curator_topic", required=True, help="RPC topic for curator"),
    cfg.StrOpt(
        "worker_host", default=socket.gethostname(), help="Compute node hostname"
    ),
]
CONF.register_opts(compute_opts, group="worker")

CONF(default_config_files=["/app/ikaros.conf"])

WORKER_TOPIC_PREFIX = "worker-"
# Initialize Oslo Messaging transport
transport = oslo_messaging.get_rpc_transport(CONF, url=CONF.worker.transport_url)
target = oslo_messaging.Target(
    topic=CONF.worker.curator_topic, namespace="curator", version="2.0"
)
client = oslo_messaging.get_rpc_client(transport, target, version_cap="2.0")
host = WORKER_TOPIC_PREFIX + CONF.worker.worker_host


def register_compute():
    """Registers the compute node with the curator."""
    node_data = {
        "host": host,
        "vcpus": 4,  # Example value
        "memory_mb": 8192,  # Example value
        "disk_gb": 100,  # Example value
    }
    response = client.call({}, "register_compute_node", node_data=node_data)
    print(f"Compute node registered: {response}")


def send_heartbeat():
    """Sends periodic heartbeats to the curator service."""
    while True:
        node_data = {"host": host}
        response = client.call({}, "heartbeat", node_data=node_data)
        print(f"Heartbeat sent: {response}")
        time.sleep(30)  # Send a heartbeat every 30 seconds


if __name__ == "__main__":
    register_compute()
    send_heartbeat()
