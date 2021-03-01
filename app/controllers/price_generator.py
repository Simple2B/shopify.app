import requests
from flask import current_app
from requests.auth import HTTPBasicAuth
from app.shopify_api import Product


def price_generator(purchase_price, mom=None, margin=None, round_to=None):
    """Generate new price

    Args:
        purchase_price (str or int): Purchase price
        mom (str or int, optional): Price at Mall of Master. Defaults to None.
        margin (str or int, optional): Margin procent. Defaults to None.
        round_to (str or int, optional): Round to (e.g. xx.99) Defaults to None.

    Returns:
        [dict]: Data for update product price
    """
    new_price = None
    if mom:
        if float(purchase_price) * (float(margin)/100+1) > float(mom):
            new_price = float(purchase_price) * (float(margin)/100+1)
        else:
            new_price = float(mom) - 0.01
    elif margin:
        new_price = float(purchase_price) * (float(margin)/100+1)
    elif round_to:
        new_price = round(float(purchase_price)) - (1 - float(round_to))
    return {'product': {'price': str(new_price)}}


def get_purchase_price(item_id):
    """Get purchase price from VidaXL

    Args:
        item_id (int or str):

    Returns:
        Str: Purchase price
    """
    response = requests.get(
        f"https://b2b.vidaxl.com/api_customer/products?code_eq={item_id}",
        auth=HTTPBasicAuth(
            current_app.config["USER_NAME"], current_app.config["API_KEY"]
        ),
    )
    if response.status_code == 200:
        return response.json()['data'][0]['price']
    else:
        return f"Statucs code: {response.status_code}"


def set_price(item_id, price, token, url):
    data = {'product': {'price': str(price)}}
    new_product = Product(token, url)
    new_product.update_product(item_id, data)
    if response.status_code == 200:
        return f'Price item {item_id} has been changed.'
    else:
        return f"Statucs code: {response.status_code}"
