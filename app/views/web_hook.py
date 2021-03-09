from flask import Blueprint, url_for, redirect, request, jsonify
from app.controllers import shopify_auth_required

hooks_blueprint = Blueprint("web_hooks", __name__)


@hooks_blueprint.route("/on_order_create")
@shopify_auth_required
def on_order_create():
    assert request
    return jsonify("OK")
