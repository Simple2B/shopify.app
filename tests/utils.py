from app.models.category import Category
import os
from app.models import Shop, Product

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data")
CATEGORIES_FILE = os.path.join(DATA_FOLDER, "categories.txt")


def fill_db_by_test_data():
    shop = Shop(name="Test Shop").save()
    categories = [
        "Toys & Games/Toys/Kids Riding Vehicles/Push & Pedal Riding Vehicles",
        "Animals & Pet Supplies/Pet Supplies/Cat Supplies/Cat Beds",
        "Animals & Pet Supplies/Pet Supplies/Dog Supplies/Dog Apparel",
        "Animals & Pet Supplies/Pet Supplies/Dog Supplies/Dog Beds",
    ]
    for i in range(10):
        Product(
            sku=f"{100089 + i}",
            title=f"Test Product({i + 1})",
            category_path=categories[i % len(categories)],
            price=((i + 1) * 1.01),
            qty=i+1,
            vidaxl_id=35084+i
        ).save()
    Category(shop_id=shop.id, path=categories[1]).save()
    Category(shop_id=shop.id, path=categories[2]).save()
