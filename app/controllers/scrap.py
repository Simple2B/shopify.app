import urllib
import time
from datetime import datetime
from urllib.request import Request, urlopen
from flask import current_app
from bs4 import BeautifulSoup
from app.models import Product, Image
from app.logger import log


def get_html(vidaxl_id: int):
    URL = f"https://b2b.vidaxl.com/products/view/{vidaxl_id}"
    # log(log.INFO, "Scraper: GET URL: [%s]", URL)
    req = Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    html = urlopen(req)
    return html


def check_soup(vidaxl_id: int):
    try:
        soup = BeautifulSoup(get_html(vidaxl_id), "html.parser")
        return soup
    except urllib.error.HTTPError:
        # log(log.WARNING, "urllib.error.HTTPError")
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
        return {"item_id": product.vidaxl_id, "qty": len(images), "images": images}
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
            return {"item_id": product.vidaxl_id, "qty": len(images), "images": images}
        log(
            log.INFO,
            "Scraping pictures: Invalid Response. Attempt: %d(%d) timeout:%s",
            i + 2,
            attempts,
            timeout,
        )
        time.sleep(timeout)
        timeout += timeout/2


def scrappy_all_products(products_number=None):
    if products_number:
        products = Product.query.limit(products_number).all()
    else:
        products = Product.query.all()
    assert products
    start_time = datetime.now()
    for i, prod in enumerate(products):
        imgs = scrap_img(prod.vidaxl_id)
        assert imgs
        log(log.INFO, imgs)
    difference_time = datetime.now() - start_time
    log(
        log.INFO,
        "Total seconds: [%d] for %d products",
        difference_time.seconds,
        products_number,
    )
