import urllib
import time
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from flask import current_app
from app.models import Configuration
from config import BaseConfig as conf
from app.logger import log


def get_price(product, shop_id):
    """Launch price gen with config parameters

    Args:
        product ([Product]): Product at DB
        shop_id (int): shop identifier

    Returns:
        [float]: Finish price
    """
    mom_selector = Configuration.get_value(
        shop_id, "MOM_SELECTOR", product.category_path
    )
    margin_percent = Configuration.get_value(
        shop_id, "MARGIN_PERCENT", product.category_path
    )
    if mom_selector:
        round_to = Configuration.get_value(shop_id, "ROUND_TO", product.category_path)
        mom_price = get_mom_price(product.sku)
        if mom_price is not None:
            return price_generator(
                purchase_price=product.price,
                margin=margin_percent,
                mom_price=mom_price,
                mom=True,
                round_to=round_to,
            )
    return price_generator(
        product.price,
        margin=margin_percent,
    )


def get_html(item_id: int):
    req = Request(
        f"https://www.mallofmaster.nl/catalogsearch/result/?q={item_id}",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    html = urlopen(req)
    return html


def scrap_price(item_id: int):
    """Get price from Mall of Master NL

    Args:
        item_id (int): Code item in VidaXL, SKU in Mall of Master

    Returns:
        [int]: [Price]
    """
    try:
        soup = BeautifulSoup(get_html(item_id), "html.parser")
    except urllib.error.HTTPError as e:
        log(log.ERROR, "Invalid response [%s]", e)
        return None
    price = soup.find("span", class_="price")
    if price:
        return float(price.string[2:].replace(",", "."))
    return None


def get_mom_price(product_id):
    """Scrap price from response

    Args:
        product_id ([int]): Product ID

    Returns:
        MoM price
    """

    for i in range(int(conf.RETRY_ATTEMPTS_NUMBER)):
        price = scrap_price(product_id)
        if price is not None:
            return price
        time.sleep(conf.SLEEP_TIME)
    log(
        log.WARNING,
        "Service Mall of Master not responding or product [%s] not registered on MoM",
        product_id,
    )
    return None


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
            if mom_price > 1:
                new_price = str(mom_price - 1)[:-2] + str(round_to)
            else:
                new_price = float(purchase_price) * (float(margin) / 100 + 1)
    elif margin:
        new_price = float(purchase_price) * (float(margin) / 100 + 1)
    return round(float(new_price), 2)
