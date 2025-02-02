from oslo_config import cfg
import oslo_messaging
import json
from datetime import datetime

from worker.api.worker import Worker
from database.database import get_session

# Define configuration options
CONF = cfg.CONF

curator_opts = [
    cfg.StrOpt('rabbitmq_host', required=True, help='RabbitMQ server hostname for curator'),
    cfg.StrOpt('transport_url', required=True, help='RabbitMQ transport URL for curator'),
    cfg.StrOpt('topic', required=True, help='RPC topic for curator')
]
CONF.register_opts(curator_opts, group='curator')

CONF(default_config_files=['/app/ikaros.conf'])

transport = oslo_messaging.get_rpc_transport(CONF, url=CONF.curator.transport_url)
target = oslo_messaging.Target(topic=CONF.curator.topic, server='curator-service')

# Mock database for compute nodes
compute_nodes = {}

class ConductorService:
    """Nova Conductor Service for managing compute node registration."""
    target = oslo_messaging.Target(namespace='curator', version='2.0')

    def get_node_by_hostname(self, context, worker_hostname):
        print(f"Finding worker {worker_hostname}")
        return Worker.get_by_hostname(context, worker_hostname)
    
    def update_host_status(self, context, worker_node):
        if worker_node:
            worker_node.last_seen = datetime.utcnow()
            worker_node.state = "up"
            worker_node.save()
            return {"status":"updated","node":worker_node.hostname}
        
    def register_compute_node(self, context, node_data):
        """Registers a new compute node."""
        worker_hostname = node_data.get("host", "unknown")
        if not (worker_hostname):
            return {"status": "error", "message":"Missing host id"}
        
        worker_node = self.get_node_by_hostname(context, worker_hostname)
        if worker_node:
            return self.update_host_status(context,worker_node)
        
        worker_node = Worker(
            {},
            hostname = worker_hostname,
            vcpus = node_data.get("vcpus", 0),
            memory_mb = node_data.get("memory_mb", 0),
            disk_gb = node_data.get("disk_gb", 0),
            gpus = "0",
            state = "up",
            last_seen = datetime.utcnow()
        )
        
        worker_node.create()

        print(f"Registered compute node: {worker_hostname}")
        return {"status": "registered", "node": worker_hostname}
    
    def list_nodes(self, context):
        if context['is_admin']:
            workers = Worker.list_all(context)
            workers = [{
                "hostname": worker.hostname,
                "vcpus": worker.vcpus,
                "gpus": worker.gpus,
                "memory_mb": worker.memory_mb,
                "disk_gb": worker.disk_gb,
                "state": worker.state,
                "last_seen": worker.last_seen
            } for worker in workers]
            return workers
        else:
            return {"nodes":""}
        
    def heartbeat(self, context, node_data):
        """Receives heartbeats from compute nodes."""
        worker_hostname = node_data.get("host", "unknown")
        if not worker_hostname:
            return {"status": "error", "message":"Missing host id"}
        worker_node = self.get_node_by_hostname(context, worker_hostname)
        if worker_node:
            return self.update_host_status(context,worker_node)
        else:
            print(f"Unknown node {worker_hostname} sending heartbeat!")
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
