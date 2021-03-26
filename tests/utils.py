import os
from random import randint
from app import db
from app.models import Shop, Product, Category, Image, Configuration

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data")
CATEGORIES_FILE = os.path.join(DATA_FOLDER, "categories.txt")


def fill_db_by_test_data():
    shop = Shop(name="Test Shop").save()
    images = [
        "https://vdxl.im/8718475964735_a_en_hd_1.jpg",
        "https://vdxl.im/8718475964735_g_en_hd_1.jpg",
        "https://vdxl.im/8718475964735_g_en_hd_2.jpg",
        "https://vdxl.im/8718475964735_g_en_hd_3.jpg",
        "https://vdxl.im/8718475964735_g_en_hd_4.jpg",
    ]
    categories = [
        "Toys & Games/Toys/Kids Riding Vehicles/Push & Pedal Riding Vehicles",
        "Animals & Pet Supplies/Pet Supplies/Cat Supplies/Cat Beds",
        "Animals & Pet Supplies/Pet Supplies/Dog Supplies/Dog Apparel",
        "Animals & Pet Supplies/Pet Supplies/Dog Supplies/Dog Beds",
    ]
    description = "<p>This memory foam neck pillow will surely bring you"
    description += "a soft velvety feel and a comfortable sleeping experience at home."
    description += "</p><ul><li>Colour: White<br/></li><li>Dimensions: 50 x 30 x (7-10) cm (L x W x H)<br/></li>"
    description += "<li>Delivery includes 2 pcs of pillow</li><li>Fabric: Polyester: 100%</li></ul>(product_id: 2899)"
    for i in range(10):
        Product(
            sku=f"{100089 + i}",
            title=f"Test Product({i + 1})",
            category_path=categories[i % len(categories)],
            price=((i + 1) * 1.01),
            qty=i + 1,
            vidaxl_id=35084 + i,
            description=description
        ).save(commit=False)
        Image(product_id=i + 1, url=randint(0, len(images))).save(commit=False)

    Category(shop_id=shop.id, path=categories[1]).save(commit=False)
    Category(shop_id=shop.id, path=categories[2]).save(commit=False)
    Configuration.set_value(shop_id=shop.id, name='MARGIN_PERCENT', value='20', path=categories[0])
    Configuration.set_value(shop_id=shop.id, name='ROUND_TO', value='95', path=categories[1])
    Configuration.set_value(shop_id=shop.id, name='LEAVE_VIDAXL_PREFIX', value=True, path=categories[2])

    db.session.commit()
