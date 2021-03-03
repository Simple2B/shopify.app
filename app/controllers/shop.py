from app.models import Shop


def update_access_token(shop_id: int, access_token: str):
    shop = Shop.query.get(shop_id)
    shop.access_token = access_token
    shop.save()
