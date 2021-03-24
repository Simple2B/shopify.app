import urllib
import time
from datetime import datetime
from urllib.request import Request, urlopen
from flask import current_app
from bs4 import BeautifulSoup
from app.models import Product, Image
from app.logger import log
from config import BaseConfig as conf


def get_html(vidaxl_id: int):
    URL = f"{conf.VIDAXL_API_BASE_URL}/products/view/{vidaxl_id}"
    req = Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    try:
        html = urlopen(req)
        return html
    except urllib.error.URLError:
        log(log.ERROR, "VidaXL server not responding")
        return None


def check_soup(vidaxl_id: int):
    try:
        soup = BeautifulSoup(get_html(vidaxl_id), "html.parser")
        return soup
    except TypeError:
        log(log.WARNING, "Wrong parser data")
        return None


def scrap_img(product):
    """Get all item pictures from VidaXL

    Args:
        Product (class)

    Returns:
        [JSON]: vidaxl_id, images quantity, list of images urls
    """
    images = Product.query.get(product.id).images
    if images:
        return [image.url for image in images]
    timeout = current_app.config["SLEEP_TIME"]
    attempts = int(current_app.config["NUMBER_OF_REPETITIONS"])
    for i in range(attempts):
        soup = check_soup(product.vidaxl_id)
        if soup:
            gallery = soup.find("div", class_="media-gallery")
            img_container = gallery.findAll("a")
            images = [
                i.attrs["href"] for i in img_container if "missing_image" not in i
            ]
            for img in images:
                Image(product_id=product.id, url=img).save()
            return images
        log(
            log.INFO,
            "Scraping pictures: Invalid Response. Attempt: %d(%d) timeout:%s",
            i + 2,
            attempts,
            timeout,
        )
        time.sleep(timeout)
        timeout += timeout/2
    return None


def scrap_description(product):
    """Get product description

    Args:
        Product ([class]): [Product]

    Returns:
        [str]: [<p> description </p>, <ul> specification_list </ul>]
    """
    if product.description:
        return product.description
    timeout = current_app.config["SLEEP_TIME"]
    attempts = int(current_app.config["NUMBER_OF_REPETITIONS"])
    for i in range(attempts):
        soup = check_soup(product.vidaxl_id)
        if soup:
            block = soup.find('div', class_='panel-body')
            description = block.p
            specification_list = block.ul
            full_description = f'{description}{specification_list}'
            product.description = full_description
            product.save()
            return full_description
        log(
            log.INFO,
            "Scraping description: Invalid Response. Attempt: %d(%d) timeout:%s",
            i + 2,
            attempts,
            timeout,
        )
        time.sleep(timeout)
        timeout += timeout/2
    return None


def scrappy_all_products(products_number=None):
    if products_number:
        products = Product.query.limit(products_number).all()
    else:
        products = Product.query.all()
    assert products
    start_time = datetime.now()
    for i, prod in enumerate(products):
        imgs = scrap_img(prod)
        assert imgs
        log(log.INFO, imgs)
    difference_time = datetime.now() - start_time
    log(
        log.INFO,
        "Total seconds: [%d] for %d products",
        difference_time.seconds,
        products_number,
    )
