from app.models import Shop


def fill_db_by_test_data():
    Shop(name="Test Shop").save()
