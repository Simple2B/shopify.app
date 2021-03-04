from flask import Blueprint, current_app

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def index():
    return current_app.config["APP_NAME"]
