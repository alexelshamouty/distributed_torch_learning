import oslo_messaging
from flask import g
from flask_restx import Namespace, Resource, fields
from oslo_config import cfg

from database.controllers.worker import Worker

#######
# Configuration
#######
CONF = cfg.CONF

compute_opts = [
    cfg.StrOpt(
        "rabbitmq_host", required=True, help="RabbitMQ server hostname for curator"
    ),
    cfg.StrOpt(
        "transport_url", required=True, help="RabbitMQ transport URL for curator"
    ),
    cfg.StrOpt("topic", required=True, help="RPC topic for curator"),
]

CONF.register_opts(compute_opts, group="curator")

# Load the configuration file
CONF(default_config_files=["/app/ikaros.conf"])
#############


###
# MOCK
###

nodes = {
    1: {"id": 1, "name": "Node A", "status": "active"},
    2: {"id": 2, "name": "Node B", "status": "active"},
}
work = {1: ["Task 1", "Task 2"], 2: ["Task 3", "Task 4"]}


job_api = Namespace("jobs", description="Job operations")
nodes_api = Namespace("nodes", description="Node management operations")

job_model = job_api.model(
    "Job",
    {
        "name": fields.String(required=True, description="The job name"),
        "github_url": fields.String(
            required=True, description="The GitHub URL of the job"
        ),
        "worker_name": fields.String(
            required=False, description="The name of the worker"
        ),
    },
)

update_model = job_api.model(
    "JobUpdate",
    {
        "name": fields.String(description="Job Name"),
        "github_url": fields.String(description="GitHub Repository URL"),
    },
)


@job_api.route("/", strict_slashes=False)
class JobCreate(Resource):
    @job_api.expect(job_model)
    def post(self):
        """Create a new job"""
        """ We will save the request to the database. And then we will put a message for the scheduler to do it's job"""
        """ After executing this a record for a job will be created in the databse. And then the scheduler will chose a host. Assign it and update the record of the task in the database"""
        return {"message": "Job created successfully"}, 201

    def get(self):
        """List all jobs"""
        return {"message": "List of jobs"}, 200


@job_api.route("/<int:job_id>", strict_slashes=False)
class JobResource(Resource):
    def delete(self, job_id):
        """Delete a job"""
        return {"message": "Job deleted successfully"}, 200

    @job_api.expect(update_model)
    def post(self, job_id):
        """Update a job"""
        return {"message": "Job updated successfully"}, 200


@nodes_api.route("/", strict_slashes=False)
class NodeList(Resource):
    def get(self):
        workers = Worker.list_all(g.context)
        workers = [
            {
                "hostname": worker.hostname,
                "vcpus": worker.vcpus,
                "gpus": worker.gpus,
                "memory_mb": worker.memory_mb,
                "disk_gb": worker.disk_gb,
                "state": worker.state,
                "last_seen": worker.last_seen.isoformat() if worker.last_seen else None,
            }
            for worker in workers
        ]
        return workers


@nodes_api.route("/<int:node_id>", strict_slashes=False)
class NodeDetail(Resource):
    def get(self, node_id):
        """Show details of a node"""
        return nodes.get(node_id, {"message": "Node not found"})


@nodes_api.route("/nodes/<int:node_id>/work")
class NodeWork(Resource):
    def get(self, node_id):
        """List work on a node"""
        return work.get(node_id, {"message": "No work found"})


@nodes_api.route("/nodes/<int:node_id>")
class NodeManagement(Resource):
    def delete(self, node_id):
        """Delete a node"""
        if node_id in nodes:
            del nodes[node_id]
            return {"message": "Node deleted"}
        return {"message": "Node not found"}, 404


@nodes_api.route("/nodes/<int:node_id>/suspend")
class NodeSuspend(Resource):
    def post(self, node_id):
        """Suspend a node"""
        if node_id in nodes:
            nodes[node_id]["status"] = "suspended"
            return {"message": "Node suspended"}
        return {"message": "Node not found"}, 404
