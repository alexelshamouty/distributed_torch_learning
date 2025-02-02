from flask import Flask
from flask_restx import Api, Resource
import threading

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

@public_ns.route('/nodes')
class NodeList(Resource):
    def get(self):
        """List all nodes"""
        return list(nodes.values())

@public_ns.route('/nodes/<int:node_id>')
class NodeDetail(Resource):
    def get(self, node_id):
        """Show details of a node"""
        return nodes.get(node_id, {'message': 'Node not found'})

@public_ns.route('/nodes/<int:node_id>/work')
class NodeWork(Resource):
    def get(self, node_id):
        """List work on a node"""
        return work.get(node_id, {'message': 'No work found'})

# Admin API Namespace
admin_ns = admin_api.namespace('admin', description='Admin API operations')

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
