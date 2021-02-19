import os
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, ".env"))


class BaseConfig(object):
    """Base configuration."""

    APP_NAME = 'Shopify_app'
    DEBUG_TB_ENABLED = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'e45f99e7dfa84f04939e041db0ee0771')
    SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY', '')
    SHOPIFY_SECRET = os.environ.get('SHOPIFY_SECRET', '')
    APP_NAME = os.environ.get('APP_NAME', '')
    SERVER_BASE_URL = os.environ.get('SERVER_BASE_URL', '')
    WEBHOOK_APP_UNINSTALL_URL = os.environ.get('WEBHOOK_APP_UNINSTALL_URL', '')
    INSTALL_REDIRECT_URL = os.environ.get('INSTALL_REDIRECT_URL', '')

    # VidaXL credentials
    VIDAXL_API_BASE_URL = os.environ.get('VIDAXL_API_BASE_URL', 'https://b2b.vidaxl.com')
    USER_NAME = os.environ.get('USER_NAME', '')
    API_KEY = os.environ.get('API_KEY', '')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

    @staticmethod
    def configure(app):
        # Implement this method to do further configuration on your app.
        pass


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEVEL_DATABASE_URL', 'sqlite:///' + os.path.join(base_dir, 'database-devel.sqlite3'))


class TestingConfig(BaseConfig):
    """Testing configuration."""

    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL', 'sqlite:///' + os.path.join(base_dir, 'database-test.sqlite3'))


class ProductionConfig(BaseConfig):
    """Production configuration."""

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///' + os.path.join(base_dir, 'database.sqlite3'))
    WTF_CSRF_ENABLED = True


config = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig)
