import urllib
import time
from urllib.request import Request, urlopen
from flask import current_app
from bs4 import BeautifulSoup
from app.logger import log


def get_html(item_id: int):
    req = Request('https://b2b.vidaxl.com/products/view/' + str(item_id), headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req)
    return html


def check_soup(item_id: int):
    try:
        soup = BeautifulSoup(get_html(item_id), 'html.parser')
        return soup
    except urllib.error.HTTPError:
        return False


def scrap_img(item_id: int):
    """Get all item pictures from VidaXL

    Args:
        item_id (int): Item_id in VidaXL API

    Returns:
        [JSON]: Item_id, images quantity, list of images urls
    """
    for i in range(int(current_app.config['NUMBER_OF_REPETITIONS'])):
        soup = check_soup(item_id)
        if soup:
            gallery = soup.find('div', class_='media-gallery')
            img_container = gallery.findAll('a')
            images = [i.attrs['href'] for i in img_container if 'missing_image' not in i]
            return {
                    'item_id': item_id,
                    'qty': len(images),
                    'images': images
                    }
        elif i == int(current_app.config['NUMBER_OF_REPETITIONS']) - 1:
            log(log.EXCEPTION, 'Server is not available')
            return False
        log(log.INFO, 'Invalid Response')
        time.sleep(int(current_app.config['SLEEP_TIME']))
