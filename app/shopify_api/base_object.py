from app.models import Shop
from config import BaseConfig as conf


class ShopifyBase(object):
    BASE_URL = conf.SHOPIFY_DOMAIN
    VERSION_API = conf.VERSION_API

    @staticmethod
    def headers(shop_id: int) -> dict:
        shop = Shop.query.get(shop_id)
        return {"X-Shopify-Access-Token": shop.access_token}
