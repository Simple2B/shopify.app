from app.models import Shop, Configuration


def update_access_token(shop_id: int, access_token: str):
    shop = Shop.query.get(shop_id)
    shop.private_app_access_token = access_token
    shop.save()


def set_csv_url(csv_url: str):
    Configuration.set_value(shop_id=1, name="CSV_URL", value=csv_url)


def get_csv_url() -> str:
    return Configuration.get_value(shop_id=1, name="CSV_URL")
