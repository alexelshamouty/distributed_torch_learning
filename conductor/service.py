from oslo_config import cfg
import oslo_messaging
import json
import time

# Define configuration options
CONF = cfg.CONF

curator_opts = [
    cfg.StrOpt('rabbitmq_host', required=True, help='RabbitMQ server hostname for curator'),
    cfg.StrOpt('transport_url', required=True, help='RabbitMQ transport URL for curator'),
    cfg.StrOpt('topic', required=True, help='RPC topic for curator')
]
CONF.register_opts(curator_opts, group='curator')

CONF(default_config_files=['../ikaros.conf'])

transport = oslo_messaging.get_rpc_transport(CONF, url=CONF.curator.transport_url)
target = oslo_messaging.Target(topic=CONF.curator.topic, server='curator-service')

# Mock database for compute nodes
compute_nodes = {}

class ConductorService:
    """Nova Conductor Service for managing compute node registration."""
    target = oslo_messaging.Target(namespace='curator', version='2.0')

    def register_compute_node(self, context, node_data):
        """Registers a new compute node."""
        node_id = node_data.get("host", "unknown")
        compute_nodes[node_id] = {
            "vcpus": node_data.get("vcpus", 0),
            "memory_mb": node_data.get("memory_mb", 0),
            "disk_gb": node_data.get("disk_gb", 0),
            "state": "up",
            "last_seen": time.time()
        }
        print(f"Registered compute node: {node_id}")
        return {"status": "registered", "node": node_id}

    def heartbeat(self, context, node_data):
        """Receives heartbeats from compute nodes."""
        node_id = node_data.get("host")
        if node_id in compute_nodes:
            compute_nodes[node_id]["last_seen"] = time.time()
            compute_nodes[node_id]["state"] = "up"
            print(f"Heartbeat received from {node_id}")
        else:
            print(f"Unknown node {node_id} sending heartbeat!")
        return {"status": "heartbeat received"}

def start_conductor():
    """Starts the Oslo Messaging conductor service."""
    endpoints = [ConductorService()]
    server = oslo_messaging.get_rpc_server(transport, target, endpoints)
    
    print("Conductor service started. Listening for compute node registrations...")
    print(f"Starting curator with {CONF.curator.transport_url} and {CONF.curator.topic}")

    try:
        print("Curator service started. Listening for compute node registrations...")
        server.start()
        server.wait()
    except KeyboardInterrupt:
        print("Shutting down Curator service...")
    finally:
        server.stop()
        server.wait()  # Ensures clean shutdown

if __name__ == '__main__':
    start_conductor()
