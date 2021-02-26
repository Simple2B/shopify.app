from flask import current_app


class BaseObject(object):
    def __init__(self):
        self.headers = {"X-Shopify-Access-Token": current_app.config['X_SHOPIFY_ACCESS_TOKEN']}
        self.base_url = current_app.config['SHOPIFY_DOMAIN']
        self.version_api = current_app.config['VERSION_API']
