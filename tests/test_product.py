import pytest
import os
import tempfile
import csv
from io import TextIOWrapper

from app import db, create_app
from app.controllers import upload_csv
from tests.utils import fill_db_by_test_data
from config import BaseConfig as conf


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


@pytest.mark.skip
def test_update_db(client):
    csv_url = conf["CSV_URL"]
    res = upload_csv(csv_url, limit=10)
    assert res


def test_upload_csv(client):
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['Name', 'Sphere', 'Date'])
        csv_writer.writerow(['John Smith', 'Accounting', 'November'])
        csv_writer.writerow(['Erica Meyers', 'IT', 'March'])
        csv_file.close()
        with open(csv_file.name, "rb") as f:
            csv_dict_reader = csv.DictReader(
                TextIOWrapper(f, encoding='utf-8'), delimiter=","
            )
            for row in csv_dict_reader:
                assert csv_dict_reader
        os.remove(csv_file.name)
