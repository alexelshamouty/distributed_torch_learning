from flask import Flask, g
from flask_restx import Api, Resource
import threading
from oslo_config import cfg
import oslo_messaging
from authenticate import authenticate_request

# Initialize Flask applications
public_app = Flask(__name__)
admin_app = Flask(__name__)

# Create API objects
public_api = Api(public_app, version='1.0', title='Public API', description='Public-facing API')
admin_api = Api(admin_app, version='1.0', title='Admin API', description='Admin API for node management')

# Mock data
nodes = {
    1: {'id': 1, 'name': 'Node A', 'status': 'active'},
    2: {'id': 2, 'name': 'Node B', 'status': 'active'}
}
work = {
    1: ['Task 1', 'Task 2'],
    2: ['Task 3', 'Task 4']
}

# Public API Namespace
public_ns = public_api.namespace('public', description='Public API operations')
# Admin API Namespace
admin_ns = admin_api.namespace('admin', description='Admin API operations')

CONF = cfg.CONF

compute_opts = [
    cfg.StrOpt('rabbitmq_host', required=True, help='RabbitMQ server hostname for curator'),
    cfg.StrOpt('transport_url', required=True, help='RabbitMQ transport URL for curator'),
    cfg.StrOpt('topic', required=True, help='RPC topic for curator')
]

CONF.register_opts(compute_opts, group='curator')

# Load the configuration file
CONF(default_config_files=['/app/ikaros.conf'])


@admin_app.before_request
@public_app.before_request
def before_request():
    authenticate_request()
    
@public_ns.route('/nodes')
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

@admin_ns.route('/nodes/<int:node_id>')
class NodeDetail(Resource):
    def get(self, node_id):
        """Show details of a node"""
        return nodes.get(node_id, {'message': 'Node not found'})

@admin_ns.route('/nodes/<int:node_id>/work')
class NodeWork(Resource):
    def get(self, node_id):
        """List work on a node"""
        return work.get(node_id, {'message': 'No work found'})

@admin_ns.route('/nodes/<int:node_id>')
class NodeManagement(Resource):
    def delete(self, node_id):
        """Delete a node"""
        if node_id in nodes:
            del nodes[node_id]
            return {'message': 'Node deleted'}
        return {'message': 'Node not found'}, 404

@admin_ns.route('/nodes/<int:node_id>/suspend')
class NodeSuspend(Resource):
    def post(self, node_id):
        """Suspend a node"""
        if node_id in nodes:
            nodes[node_id]['status'] = 'suspended'
            return {'message': 'Node suspended'}
        return {'message': 'Node not found'}, 404

# Run servers on separate ports
def run_public_api():
    public_app.run(port=5001)

def run_admin_api():
    admin_app.run(port=5002)

if __name__ == '__main__':
    threading.Thread(target=run_public_api).start()
    threading.Thread(target=run_admin_api).start()
