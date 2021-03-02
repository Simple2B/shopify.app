import os
from app.models import Shop, Product

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data")
CATEGORIES_FILE = os.path.join(DATA_FOLDER, "categories.txt")


def fill_db_by_test_data():
    Shop(name="memo-s2b-store.myshopify.com", access_token='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').save()
    categories = [
        "Toys & Games/Toys/Kids Riding Vehicles/Push & Pedal Riding Vehicles",
        "Toys & Games/Toys/Kids Riding Vehicles/Push & Pedal Riding Vehicles",
        "Animals & Pet Supplies/Pet Supplies/Cat Supplies/Cat Beds",
        "Animals & Pet Supplies/Pet Supplies/Cat Supplies/Cat Beds",
        "Animals & Pet Supplies/Pet Supplies/Cat Supplies/Cat Beds",
        "Animals & Pet Supplies/Pet Supplies/Dog Supplies/Dog Apparel",
        "Animals & Pet Supplies/Pet Supplies/Dog Supplies/Dog Apparel",
        "Animals & Pet Supplies/Pet Supplies/Dog Supplies/Dog Beds",
        "Animals & Pet Supplies/Pet Supplies/Dog Supplies/Dog Beds",
        "Animals & Pet Supplies/Pet Supplies/Dog Supplies/Dog Beds",
    ]
    for i in range(10):
        Product(
            sku=f"1000{i + 1}",
            title=f"Test Product({i + 1})",
            category_path=categories[i],
            price=(i * 1.01),
            qty=i
        ).save()
