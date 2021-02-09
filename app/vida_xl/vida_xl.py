import requests

from requests.auth import HTTPBasicAuth

from flask import current_app


def get_documents():
    # headers = {"Authorization": "Basic " + "jamilya.sars@gmail.com" + "ea5d924f-3531-4550-9e28-9ed5cf76d3f7"}

    # current_app.config["AIDAXL_API_BASE_URL"]
    response = requests.get(
        "https://b2b.vidaxl.com/api_customer/orders/documents", auth=HTTPBasicAuth('jamilya.sars@gmail.com', 'ea5d924f-3531-4550-9e28-9ed5cf76d3f7')
    )
    if response.status_code == 200:
        return response.json()
    else:
        return f'Statucs code: {response.status_code}'
    # me_json = response.json()
