from app.models import Shop


def fill_db_by_test_data():
    Shop(name="https://memo-s2b-store.myshopify.com").save()
