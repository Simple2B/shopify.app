from flask import Blueprint, current_app, request, url_for

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def index():
    # if request.args.get("shop", None):

    return current_app.config["APP_NAME"]
