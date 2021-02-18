import requests

from requests.auth import HTTPBasicAuth

from flask import current_app


def get_documents():
    # headers = {"Authorization": "Basic " + "jamilya.sars@gmail.com" + "ea5d924f-3531-4550-9e28-9ed5cf76d3f7"}

    # current_app.config["AIDAXL_API_BASE_URL"]
    # test url
    sand_box_url = "https://sandbox.b2b.vidaxl.com/"
    # end
    response = requests.get(
        f"{sand_box_url}api_customer/orders/documents",
        auth=HTTPBasicAuth(
            current_app.config["USER_NAME"], current_app.config["API_KEY"]
        ),
    )

    if response.status_code == 200:
        return response.json()
    else:
        return f"Statucs code: {response.status_code}"
    # me_json = response.json()


def get_products():
    response = requests.get(
        f"{current_app.config['VIDAXL_API_BASE_URL']}/api_customer/products",
        auth=HTTPBasicAuth(
            current_app.config["USER_NAME"], current_app.config["API_KEY"]
        ),
    )

    if response.status_code == 200:
        # return response.json()['data']
        return response.json()
    else:
        return f"Statucs code: {response.status_code}"
    # me_json = response.json()
