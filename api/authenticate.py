from flask import Flask, request, g
from oslo_context import context

def authenticate_request():
    user_id = request.headers.get('X-User-ID')

    if not user_id:
        g.context = None
        return
    
    g.context = context.RequestContext(user=user_id ,is_admin=True)