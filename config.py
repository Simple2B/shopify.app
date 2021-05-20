import os
from dotenv import load_dotenv
from app.logger import log

base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, ".env"))


class BaseConfig(object):
    """Base configuration."""

    APP_NAME = "Shopify_app"
    DEBUG_TB_ENABLED = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "e45f99e7dfa84f04939e041db0ee0771")
    SHOPIFY_API_KEY = os.environ.get("SHOPIFY_API_KEY", "")
    SHOPIFY_SECRET = os.environ.get("SHOPIFY_SECRET", "")
    APP_NAME = os.environ.get("APP_NAME", "Shopify App")
    SHOPIFY_DOMAIN = os.environ.get("SHOPIFY_DOMAIN", "")
    VERSION_API = os.environ.get("VERSION_API", "2021-01")
    WEBHOOK_APP_UNINSTALL_URL = os.environ.get("WEBHOOK_APP_UNINSTALL_URL", "")
    INSTALL_REDIRECT_URL = os.environ.get("INSTALL_REDIRECT_URL", "")
    ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "")
    NUMBER_OF_REPETITIONS = os.environ.get("NUMBER_OF_REPETITIONS", "5")
    SLEEP_TIME = float(os.environ.get("SLEEP_TIME", "1"))
    HOST_NAME = os.environ.get("HOST_NAME", "localhost")
    SHOPIFY_PRIVATE_APP_PASSWORD = os.environ.get("SHOPIFY_PRIVATE_APP_PASSWORD", "")

    # VidaXL credentials
    VIDAXL_API_BASE_URL = os.environ.get(
        "VIDAXL_API_BASE_URL", "https://b2b.vidaxl.com"
    )
    VIDAXL_USER_NAME = os.environ.get("VIDAXL_USER_NAME", "")
    VIDAXL_API_KEY = os.environ.get("VIDAXL_API_KEY", "")
    VIDAXL_SANDBOX_PASSWORD = os.environ.get("VIDAXL_SANDBOX_PASSWORD", "")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

    # Retry policy
    RETRY_ATTEMPTS_NUMBER = os.environ.get("RETRY_ATTEMPTS_NUMBER", "3")
    RETRY_TIMEOUT = os.environ.get("RETRY_TIMEOUT", "3")

    # Configuration parameters
    ADMIN_LEAVE_VIDAXL_PREFIX = os.environ.get("LEAVE_VIDAXL_PREFIX", "Y") in (
        "Y",
        "y",
        "true",
        "True",
    )
    ADMIN_MOM_SELECTOR = os.environ.get("ADMIN_MOM_SELECTOR", False)
    ADMIN_MARGIN_PERCENT = os.environ.get("ADMIN_MARGIN_PERCENT", 13)
    ADMIN_ROUND_TO = os.environ.get("ADMIN_ROUND_TO", 99)
    ADMIN_CSV_URL = os.environ.get("ADMIN_CSV_URL", "")

    CATEGORY_SPLITTER = os.environ.get("CATEGORY_SPLITTER", "/")

    TAX_COEFFICIENT = os.environ.get("TAX_COEFFICIENT", 1.21)

    @staticmethod
    def configure(app):
        # Implement this method to do further configuration on your app.
        log.set_level(int(os.environ.get("LOG_LEVEL", log.DEBUG)))


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEVEL_DATABASE_URL",
        "sqlite:///" + os.path.join(base_dir, "database-devel.sqlite3"),
    )


class TestingConfig(BaseConfig):
    """Testing configuration."""

    TESTING = True
    VIDAXL_API_BASE_URL = os.environ.get(
        "VIDAXL_API_BASE_URL", "https://b2b.vidaxl.com"
    )
    USER_NAME = os.environ.get("USER_NAME", "")
    API_KEY = os.environ.get("API_KEY", "")

    ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "")
    SHOPIFY_DOMAIN = os.environ.get("SHOPIFY_DOMAIN", "")

    # Private app
    X_SHOPIFY_ACCESS_TOKEN = os.environ.get("X_SHOPIFY_ACCESS_TOKEN", "")

    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL",
        "sqlite:///" + os.path.join(base_dir, "database-test.sqlite3"),
    )


class ProductionConfig(BaseConfig):
    """Production configuration."""

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(base_dir, "database.sqlite3")
    )
    # WTF_CSRF_ENABLED = True


config = dict(
    development=DevelopmentConfig, testing=TestingConfig, production=ProductionConfig
)
