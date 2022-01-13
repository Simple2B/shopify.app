import pytest
import os
import tempfile
import csv
from io import TextIOWrapper

from app import db, create_app
from app.controllers.products import download_vidaxl_product_from_csv
from config import BaseConfig as conf
from app.models import Product
from tests.utils import fill_db_by_test_data


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.drop_all()
        db.create_all()
        fill_db_by_test_data()
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


@pytest.mark.skipif(not conf.ADMIN_CSV_URL, reason="CSV file url is not configured")
def test_update_db(client):
    Product.query.delete()
    csv_url = conf.ADMIN_CSV_URL
    LIMIT = 10
    download_vidaxl_product_from_csv(csv_url, limit=LIMIT)
    count_products_after = Product.query.count()
    assert count_products_after == LIMIT


def test_experiments_with_csv():
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as csv_file:
        try:
            csv_writer = csv.writer(
                csv_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            csv_writer.writerow(["Name", "Sphere", "Date"])
            csv_writer.writerow(["John Smith", "Accounting", "November"])
            csv_writer.writerow(["Erica Meyers", "IT", "March"])
            csv_file.close()
            with open(csv_file.name, "rb") as f:
                csv_dict_reader = csv.DictReader(
                    TextIOWrapper(f, encoding="utf-8"), delimiter=","
                )
                for row in csv_dict_reader:
                    assert csv_dict_reader
        finally:
            os.remove(csv_file.name)


@pytest.mark.skipif(not conf.SHOPIFY_DOMAIN, reason="Shopify store is not configured")
def test_product_count(client):
    from config import BaseConfig as conf
    import requests

    url = f"{conf.SHOPIFY_DOMAIN}/admin/api/2021-10/products/count.json"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Shopify-Access-Token": conf.SHOPIFY_PRIVATE_APP_PASSWORD,
    }
    response = requests.get(url, headers=headers)
    assert response
