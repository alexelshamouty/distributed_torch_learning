from flask import Flask, g
from flask_restx import Namespace, Resource, fields
import oslo_messaging
from oslo_config import cfg


#######
# Configuration
#######
CONF = cfg.CONF

compute_opts = [
    cfg.StrOpt('rabbitmq_host', required=True, help='RabbitMQ server hostname for curator'),
    cfg.StrOpt('transport_url', required=True, help='RabbitMQ transport URL for curator'),
    cfg.StrOpt('topic', required=True, help='RPC topic for curator')
]

CONF.register_opts(compute_opts, group='curator')

# Load the configuration file
CONF(default_config_files=['/app/ikaros.conf'])
#############


###
# MOCK
###

nodes = {
    1: {'id': 1, 'name': 'Node A', 'status': 'active'},
    2: {'id': 2, 'name': 'Node B', 'status': 'active'}
}
work = {
    1: ['Task 1', 'Task 2'],
    2: ['Task 3', 'Task 4']
}


job_api = Namespace('jobs', description='Job operations')
nodes_api = Namespace('nodes', description='Node management operations')

job_model = job_api.model('Job', {
    'name': fields.String(required=True, description='The job name'),
    'github_url': fields.String(required=True, description='The GitHub URL of the job'),
    'worker_name': fields.String(required=False, description='The name of the worker'),
})

update_model = job_api.model(
    "JobUpdate",
    {
        "name": fields.String(description="Job Name"),
        "github_url": fields.String(description="GitHub Repository URL")
    }
)

@job_api.route('/', strict_slashes=False)
class JobCreate(Resource):
    @job_api.expect(job_model)
    def post(self):
        """Create a new job"""
        return {'message': 'Job created successfully'}, 201
    def get(self):
        """List all jobs"""
        return {'message': 'List of jobs'}, 200
    
@job_api.route('/<int:job_id>',strict_slashes=False)
class JobResource(Resource):
    def delete(self, job_id):
        """Delete a job"""
        return {'message': 'Job deleted successfully'}, 200
    @job_api.expect(update_model)
    def post(self, job_id):
        """Update a job"""
        return {'message': 'Job updated successfully'}, 200

@nodes_api.route('/', strict_slashes=False)
class NodeList(Resource):
    def get(self):
        context = g.context
        if not context or not context.is_admin:
            return {"message": "Unauthorized"}, 401
        """List all nodes"""
        transport = oslo_messaging.get_rpc_transport(CONF, url=CONF.curator.transport_url)
        target = oslo_messaging.Target(topic=CONF.curator.topic, namespace='curator',  version='2.0')
        client = oslo_messaging.get_rpc_client(transport, target, version_cap='2.0')
        nodes = client.call(context, 'list_nodes')
        return nodes

@nodes_api.route('/<int:node_id>', strict_slashes=False)
class NodeDetail(Resource):
    def get(self, node_id):
        """Show details of a node"""
        return nodes.get(node_id, {'message': 'Node not found'})
