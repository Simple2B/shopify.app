import urllib
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from app.logger import log


def get_html(item_id: int):
    req = Request('https://b2b.vidaxl.com/products/view/' + str(item_id), headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req)
    return html


def scrap_img(item_id: int):
    try:
        soup = BeautifulSoup(get_html(item_id), 'html.parser')
    except urllib.error.HTTPError:
        log(log.INFO, 'Invalid response')
        return False
    gallery = soup.find('div', class_='media-gallery')
    img_container = gallery.findAll('a')
    images = [i.attrs['href'] for i in img_container]
    if 'missing_image' in images:
        for img in images:
            if 'missing_image' in img:
                images.pop(img)
    return {
        'item_id': item_id,
        'qty': len(images),
        'images': images
    }
