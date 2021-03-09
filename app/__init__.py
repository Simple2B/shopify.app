import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException
from flask_migrate import Migrate
from app.logger import log

# instantiate extensions
db = SQLAlchemy()
migrate = Migrate()
log.set_level(log.DEBUG)


def create_app(environment="development"):

    from config import config
    from app.views import (
        admin_blueprint,
        shopify_blueprint,
        main_blueprint,
        hooks_blueprint,
    )

    # Instantiate app.
    app = Flask(__name__)

    # Set app config.
    env = os.environ.get("FLASK_ENV", environment)
    app.config.from_object(config[env])
    config[env].configure(app)

    # Set up extensions.
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints.
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(shopify_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(hooks_blueprint)

    # Error handlers.
    @app.errorhandler(HTTPException)
    def handle_http_error(exc):
        return render_template("error.html", error=exc), exc.code

    return app
