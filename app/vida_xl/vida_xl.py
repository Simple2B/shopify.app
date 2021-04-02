import time
import json
import requests
from requests.auth import HTTPBasicAuth

from app.logger import log
from config import BaseConfig as conf


def retry_get_request(url, auth=None, headers=None):
    time_sleep = int(conf.RETRY_TIMEOUT)
    for attempt_no in range(int(conf.RETRY_ATTEMPTS_NUMBER)):
        try:
            res = requests.get(url, auth=auth, headers=headers)
            if not res.ok:
                if attempt_no:
                    time_sleep *= 2
                log(
                    log.DEBUG,
                    "!> Retry attempt:%d request: [%s]; time sleep: [%d]",
                    attempt_no + 1,
                    url,
                    time_sleep,
                )
                time.sleep(time_sleep)
                continue
            return res
        except Exception as err:
            log(log.WARNING, "Get request error: [%s] attempt: %d", err, attempt_no + 1)
            time.sleep(int(conf.RETRY_TIMEOUT))
    log(log.ERROR, "Get request error")
    return None


def retry_post_request(url, data, auth=None, headers=None):
    time_sleep = int(conf.RETRY_TIMEOUT)
    for attempt_no in range(int(conf.RETRY_ATTEMPTS_NUMBER)):
        try:
            res = requests.post(url, auth=auth, headers=headers, json=data)
            if not res.ok:
                if attempt_no:
                    time_sleep *= 2
                log(
                    log.DEBUG,
                    "!> Retry attempt:%d request: [%s]; time sleep: [%d]",
                    attempt_no + 1,
                    url,
                    time_sleep,
                )
                time.sleep(time_sleep)
                continue
            return res
        except Exception as err:
            log(log.WARNING, "Get request error: [%s] attempt: %d", err, attempt_no + 1)
            time.sleep(int(conf.RETRY_TIMEOUT))
    log(log.ERROR, "Post request error")
    return None


class VidaXl(object):
    def __init__(self):
        self.basic_auth = HTTPBasicAuth(conf.VIDAXL_USER_NAME, conf.VIDAXL_API_KEY)
        self.sandbox_auth = HTTPBasicAuth(
            conf.VIDAXL_USER_NAME, conf.VIDAXL_SANDBOX_PASSWORD
        )
        self.base_url = f"{conf.VIDAXL_API_BASE_URL}/api_customer/products"

    def get_orders(self):
        response = retry_get_request(
            f"{conf.VIDAXL_API_BASE_URL}/api_customer/orders.json", auth=self.basic_auth
        )
        if response.status_code == 200:
            log(log.INFO, "%s", response.text)
            return json.loads(response.text)
        else:
            log(log.ERROR, "Invalid response, status code: [%s]", response.status_code)
            return None

    def get_invoice(self, order_id):
        response = retry_get_request(
            f"{conf.VIDAXL_API_BASE_URL}/api_customer/orders/{order_id}/documents",
            auth=self.basic_auth,
        )
        if response.status_code == 200:
            log(log.INFO, "%s", response.text)
            return json.loads(response.text)
        else:
            log(log.ERROR, "Invalid response, status code: [%s]", response.status_code)
            return None

    def get_product(self, item_id):
        resp = retry_get_request(
            f"{self.base_url}?code_eq={item_id}", auth=self.basic_auth
        )
        if not resp.status_code == 200:
            log(log.ERROR, "Invalid response, status code: [%s]", resp.status_code)
            return None
        # log(log.DEBUG, f"Response: {resp}")
        data = resp.json()
        if not data or "data" not in data:
            log(log.ERROR, "VidaXl: Invalid data for item: [%s]", item_id)
            return None
        data = data["data"]
        if not data:
            log(log.ERROR, "VidaXl: No data for item: [%s]", item_id)
            return None
        return data[0]

    def create_order(self, order_data):
        if order_data:
            response = retry_post_request(
                f"{conf.VIDAXL_API_BASE_URL}/api_customer/orders",
                auth=self.basic_auth,
                data=order_data,
            )
            if response:
                log(log.INFO, "%s", response.text)
                log(log.INFO, "Order was created.")
                return json.loads(response.text)
            else:
                log(log.ERROR, "Invalid response from VidaXL")
                return None

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
        percents_done = 0
        count_done = 0

        def update_progress():
            nonlocal count_done, percents_done
            count_done += 1
            new_percents = count_done * 100 // total_products
            if new_percents - percents_done >= 10:
                percents_done = new_percents
                log(log.INFO, "Progress: %d%%", percents_done)

        for product in products:
            update_progress()
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
                    update_progress()
                    yield product
