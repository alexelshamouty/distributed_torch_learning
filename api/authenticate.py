from flask import Flask, g, request
from oslo_context import context


def authenticate_request():
    user_id = request.headers.get("X-User-ID")

    if not user_id:
        g.context = None
        return

    g.context = context.RequestContext(user=user_id, is_admin=True)


def authenticate_admin():
    context = g.context
    if not context or not context.is_admin:
        return {"message": "Unauthorized"}, 401
