import urllib
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from app.logger import log


def get_html(item_id: int):
    req = Request(
        'https://www.mallofmaster.nl/catalogsearch/result/?q=' +
        str(item_id), headers={'User-Agent': 'Mozilla/5.0'}
        )
    html = urlopen(req)
    return html


def scrap_price(item_id: int):
    """Get price from Mall of Master NL

    Args:
        item_id (int): Code item in VidaXL, SKU in Mall of Master

    Returns:
        [int]: Price in Euro
    """
    try:
        soup = BeautifulSoup(get_html(item_id), 'html.parser')
    except urllib.error.HTTPError as e:
        log(log.ERROR, 'Invalid response [%s]', e)
        return False
    price = soup.find('span', class_='price')
    return int(price.string[2:])
