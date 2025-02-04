from flask import Flask, g
from flask_restx import Api, Resource
import threading
from oslo_config import cfg
import oslo_messaging
from authenticate import authenticate_request
from models.api import job_api as job_api
from models.api import nodes_api as nodes_api

# Initialize Flask applications
public_app = Flask(__name__)
admin_app = Flask(__name__)

# Create API objects
public_api = Api(public_app, version='1.0', title='Public API', description='Public-facing API')
admin_api = Api(admin_app, version='1.0', title='Admin API', description='Admin API for node management')

# Adding namespaces to APIs
public_api.add_namespace(job_api)
public_api.add_namespace(nodes_api)
admin_api.add_namespace(nodes_api)

# Authenticate and set a generic context for now
@admin_app.before_request
@public_app.before_request
def before_request():
    authenticate_request()

# Run servers on separate ports
def run_public_api():
    public_app.run(port=5001, host='0.0.0.0')

def run_admin_api():
    admin_app.run(port=5002, host='0.0.0.0')

if __name__ == '__main__':
    threading.Thread(target=run_public_api).start()
    threading.Thread(target=run_admin_api).start()
