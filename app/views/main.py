from flask import Blueprint, url_for, redirect, request
from app.controllers import shopify_auth_required

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
@shopify_auth_required
def index():
    return redirect(url_for("admin.admin", **request.args))
