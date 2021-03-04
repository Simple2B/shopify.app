import requests
import time
from requests.auth import HTTPBasicAuth
from flask import current_app
from app.logger import log


def get_price(product):
    """Launch price gen with config parameters

    Args:
        product ([Product]): Product at DB

    Returns:
        [float]: Finish price
    """
    if current_app.config["ADMIN_MOM_SELECTOR"]:
        price = price_generator(
            product.price,
            get_mom_price(product.sku),
            mom=True,
            margin=current_app.config["ADMIN_MARGIN_PROCENT"],
            round_to=current_app.config["ADMIN_ROUND_TO"],
        )
    else:
        price = price_generator(
            product.price,
            margin=current_app.config["ADMIN_MARGIN_PROCENT"],)
    return price


def get_response_from_mom(product_id):
    """Get response from service Mall of Master

    Args:
        product_id (int or str): Product ID

    Returns:
        Response
    """
    response = requests.get(
        f"https://b2b.vidaxl.com/api_customer/products?code_eq={product_id}",
        auth=HTTPBasicAuth(
            current_app.config["VIDAXL_USER_NAME"], current_app.config["VIDAXL_API_KEY"]
        ),
    )
    if response.status_code == 200:
        return response.json()
    else:
        log(log.ERROR, "Invalid response [%s]", response.status_code)
        return False


def get_mom_price(product_id):
    """Scrap price from response

    Args:
        product_id ([int]): Product ID

    Returns:
        MoM price
    """
    for i in range(current_app.config["NUMBER_OF_REPETITIONS"]):
        response = get_response_from_mom(product_id)
        if response:
            return response["data"][0]["price"]
        time.sleep(current_app.config["SLEEP_TIME"])
    log(log.ERROR, "Service Mall of Master not responding")
    return False


def price_generator(purchase_price, margin, mom_price=None, mom=None, round_to=None):
    """Generate new price

    Args:
        purchase_price (str or int): Purchase price.
        mom_price (str or int): Price at Mall of Master.
        margin (str or int): Margin procent. (e.g. 20, 10, 15, 50, 100)
        mom (str or int, optional): Price at Mall of Master. Defaults to None.
        round_to (str or int, optional): Round to (e.g. 99, 95, 50) Defaults to None.

    Returns:
        [float]: Calculated price.
    """
    new_price = None
    if mom:
        if float(purchase_price) > float(mom_price):
            new_price = float(purchase_price) * (float(margin) / 100 + 1)
        else:
            if mom > 1:
                new_price = str(mom_price - 1)[:-2] + str(round_to)
            else:
                new_price = float(purchase_price) * (float(margin) / 100 + 1)
    elif margin:
        new_price = float(purchase_price) * (float(margin) / 100 + 1)
    return float(new_price)
