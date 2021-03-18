import requests
from config import BaseConfig as conf
from app.logger import log


def delete_order(order_id):
    """[Delete order by ID]

    Args:
        order_id ([str or int]): [Order ID]

    Returns:
        [Bool]: [Shopify response]
    """
    url = f'{conf.SHOPIFY_DOMAIN}/admin/api/2021-01/orders/{order_id}/cancel.json'
    headers = {
        'User-Agent': 'Mozilla/5.0',
        "X-Shopify-Access-Token": conf.SHOPIFY_PRIVATE_APP_PASSWORD
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        log(log.INFO, 'Order with ID [%d] deleted.', order_id)
        return True
    else:
        log(log.ERROR, 'Invalid response from Shopify, code [%d]', response.status_code)
        return False
