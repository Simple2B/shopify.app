import time

import requests
from requests.auth import HTTPBasicAuth

from app.logger import log
from config import BaseConfig as conf


def retry_get_request(url, auth=None, headers=None):
    time_sleep = conf.RETRY_TIMEOUT
    time.sleep(time_sleep)
    for attempt_no in range(conf.RETRY_ATTEMPTS_NUMBER):
        try:
            res = requests.get(url, auth=auth, headers=headers)
            if not res.ok:
                if attempt_no:
                    time_sleep *= 2
                log(log.DEBUG, "!> Retry attempt:%d request: [%s]; time sleep: [%d]", attempt_no + 1, url, time_sleep)
                time.sleep(time_sleep)
                continue
            return res
        except Exception as err:
            log(log.WARNING, "Get request error: [%s] attempt: %d", err, attempt_no + 1)
            time.sleep(conf.RETRY_TIMEOUT)
    log(log.ERROR, "Get request error")
    return None


class VidaXl(object):
    def __init__(self):
        self.basic_auth = HTTPBasicAuth(conf.VIDAXL_USER_NAME, conf.VIDAXL_API_KEY)
        self.base_url = f"{conf.VIDAXL_API_BASE_URL}/api_customer/products"

    def get_documents(self):
        sand_box_url = "https://sandbox.b2b.vidaxl.com/"
        response = retry_get_request(
            f"{sand_box_url}api_customer/orders/documents", auth=self.basic_auth
        )

        if response.status_code == 200:
            return response.json()
        else:
            return f"Statucs code: {response.status_code}"

    def get_product(self, item_id):
        resp = retry_get_request(
            f"{self.base_url}?code_eq={item_id}", auth=self.basic_auth
        )
        if not resp.status_code == 200:
            log(log.ERROR, "Invalid response, status code: [%s]", resp.stack_code)
        log(log.DEBUG, f"Response: {resp}")
        return resp.json()

    @property
    def products(self):
        LIMIT = 500
        offset = 0
        response = retry_get_request(
            f"{self.base_url}?offset={offset}&limit={LIMIT}", auth=self.basic_auth
        )
        if not response or not response.status_code == 200:
            log(log.ERROR, "Invalid response, status code: [%s]", response.status_code)
            return None
        data = response.json()
        total_products = data["pagination"]["total"]
        LIMIT = min(LIMIT, data["pagination"]["limit"])
        log(log.INFO, "Get total products: [%d]", total_products)
        products = data["data"]
        for product in products:
            yield product
        if total_products > LIMIT:
            range_ = (total_products - LIMIT) // LIMIT
            for i in range(range_ + 1 if (total_products % LIMIT) != 0 else range_):
                response = retry_get_request(
                    f"{self.base_url}?offset={LIMIT*(i+1)}&limit={LIMIT}",
                    auth=self.basic_auth,
                )
                if not response or not response.status_code == 200:
                    log(
                        log.ERROR,
                        "Invalid response, status code: [%s]",
                        response.status_code,
                    )
                    return None
                data = response.json()
                products = data["data"]
                for product in products:
                    yield product
