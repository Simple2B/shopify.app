import time
import requests
from config import BaseConfig as conf
from app.logger import log


def retry_get_request(url, auth=None):
    for attempt_no in range(conf.RETRY_ATTEMPTS_NUMBER):
        try:
            res = requests.get(url, auth=auth)
            if not res.ok:
                time.sleep(conf.RETRY_TIMEOUT)
                continue
            return res
        except Exception as err:
            log(log.WARNING, "Get request error: [%s] attempt: %d", err, attempt_no)
            time.sleep(conf.RETRY_TIMEOUT)
    log(log.ERROR, "Get request error")
    return None
