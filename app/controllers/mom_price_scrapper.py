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


def price_generator(purchase_price, mom=None, margin=0, round_to=None):
    """Generate new price

    Args:
        purchase_price (str or int): Purchase price
        mom (str or int, optional): Price at Mall of Master. Defaults to None.
        margin (str or int, optional): Margin procent. Defaults to None.
        round_to (str or int, optional): Round to (e.g. xx.99) Defaults to None.

    Returns:
        [str]: Price
    """
    new_price = None
    if mom:
        if float(purchase_price) > float(mom):
            new_price = float(purchase_price) * (float(margin)/100+1)
        else:
            if mom > 1:
                new_price = str(mom-1)[:-2] + '.' + str(round_to)
            else:
                new_price = float(purchase_price) * (float(margin)/100+1)
    else:
        new_price = float(purchase_price) * (float(margin)/100+1)
    return str(new_price)
