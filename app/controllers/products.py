import tempfile
import requests
import csv
from io import TextIOWrapper
from datetime import datetime

import shopify
from app import db
from app.models import (
    Configuration,
    Category,
    Product,
    Shop,
    ShopProduct,
    Image,
    Description,
)
from .price import get_price
from .scrap import scrap_img, scrap_description
from app.logger import log
from app.vida_xl import VidaXl
from config import BaseConfig as conf


def upload_product_old(
    prod_api,
    collect_api,
    product_id,
    title,
    qty,
    price,
    collection,
):
    if not qty:
        pass
    else:
        images_src = scrap_img(product_id).get("images", "")
        if not Configuration.prefix_vidaxl:
            if title.startswith("vidaXL "):
                title = title.replace("vidaXL ", "")
        collection_id = collect_api.create_collection(
            {"custom_collection": {"title": collection}}
        )
        res = prod_api.create_product(
            {
                "product": {
                    "title": title,
                    # "body_html": "<strong>Good snowboard!</strong>",
                    # "vendor": "Burton",
                    "variants": [
                        {
                            # "option1": "First",
                            "inventory_item_id": product_id,
                            "price": price,
                            # "sku": "123"
                        }
                    ],
                    "images": [{"src": img_src} for img_src in images_src],
                },
                "status": "active",
            }
        )
        collect_api.put_product(
            {
                "collect": {
                    "product_id": res["product"]["id"],
                    "collection_id": collection_id,
                }
            }
        )
        prod_api.set_quantity(inventory_item_id=product_id, quantity=qty)
        log(log.DEBUG, "Product created. Product id: [%d]", product_id)


def upload_csv(csv_url, limit=None):

    def update_db_from_file_stream(csv_dict_reader, limit=None):
        number_db_commit = 0
        next_product_id = Product.query.count() + 1
        for i, vidaxl_prod in enumerate(csv_dict_reader):
            update_date = datetime.now()
            sku = vidaxl_prod["SKU"]
            title = vidaxl_prod["Product_title"]
            price = float(vidaxl_prod["B2B price"])
            quantity = float(vidaxl_prod["Stock"])
            category_path = vidaxl_prod["Category"]
            description = vidaxl_prod["HTML_description"]
            images = [
                vidaxl_prod[image]
                for image in vidaxl_prod
                if image.startswith("Image") and vidaxl_prod[image] != ""
            ]
            log(log.DEBUG, "Get images (%d)", len(images))
            vidaxl_id = vidaxl_prod["EAN"]
            prod = Product.query.filter(Product.sku == sku).first()
            if prod:
                if title != prod.title:
                    prod.title = title
                    prod.is_changed = True
                if category_path != prod.category_path:
                    prod.category_path = category_path
                    prod.is_changed = True
                if price != prod.price:
                    prod.price = price
                    prod.is_changed = True
                if quantity != prod.qty:
                    prod.qty = quantity
                    prod.is_changed = True
                if description != prod.description[0].text:
                    prod.description[0].text = description
                    prod.is_changed = True

                if prod.is_deleted:
                    prod.is_changed = True

                prod.updated = update_date
                prod.is_deleted = False

                # update images
                for i, image in enumerate(images):
                    if not image:
                        continue
                    try:
                        prod.images[i].url = image
                    except IndexError:
                        Image(product_id=prod.id, url=image).save(commit=False)
                        number_db_commit += 1

                prod.save(commit=False)
                number_db_commit += 1
            else:
                Product(
                    vidaxl_id=vidaxl_id,
                    sku=sku,
                    title=title,
                    category_path=category_path,
                    price=price,
                    qty=quantity,
                ).save(commit=False)
                for image in images:
                    Image(product_id=next_product_id, url=image).save(commit=False)
                Description(product_id=next_product_id, text=description).save(commit=False)
                log(log.DEBUG, "Add new product[%d: %s] to db", next_product_id, title)
                next_product_id += 1
                number_db_commit += 1
            if number_db_commit > 100:
                db.session.commit()
            if limit and i + 1 >= limit:
                db.session.commit()
                break

    with tempfile.NamedTemporaryFile(mode="w+b") as csv_file:
        response = requests.get(csv_url, stream=True)
        if response.status_code != 200:
            log(log.ERROR, "Invalid response [%s]", response)
            return None
        for chunk in response.iter_content(chunk_size=100 * 1024):
            csv_file.write(chunk)
        try:
            with open(csv_file.name, "rb") as f:
                csv_dict_reader = csv.DictReader(
                    TextIOWrapper(f, encoding="utf-8"), delimiter=","
                )
                update_db_from_file_stream(csv_dict_reader, limit)
                return True
        except Exception as exc:
            log(log.ERROR, "Invalid file; exception: (%s)", exc)
            return None
            if not f.read():
                log(log.WARNING, "CSV File is empty")
                return None


def download_products(limit=None):
    csv_url = Configuration.get_value(1, "SCV_PATH", path="/")
    if csv_url:
        return upload_csv(csv_url)
    vida = VidaXl()
    update_date = datetime.now()
    log(log.INFO, "Start update VidaXl products - %s", "All" if not limit else limit)
    updated_product_count = 0
    for prod in vida.products:
        # add product into DB
        if not update_product_db(prod, update_date):
            continue
        updated_product_count += 1
        if limit is not None and updated_product_count >= limit:
            break
    for product in (
        Product.query.filter(Product.updated < update_date)
        .filter(Product.is_deleted == False)  # noqa E712
        .all()
    ):
        product.is_deleted = True
        product.is_changed = True
        product.save()
        log(log.DEBUG, "Product code:[%s] deleted...", product.sku)
    log(
        log.INFO,
        "Updated %d products in %d seconds",
        updated_product_count,
        (datetime.now() - update_date).seconds,
    )


def update_product_db(prod, update_date=None):
    if not update_date:
        update_date = datetime.now()
    name = prod["name"]
    code = prod["code"]
    price = float(prod["price"])
    quantity = float(prod["quantity"])
    currency = prod["currency"]
    vidaxl_id = prod["id"]
    if currency != "EUR":
        log(
            log.WARNING,
            "Product code: [%s] skipped - currency: [%s]",
            code,
            currency,
        )
        return False
    category_path = prod["category_path"]
    if quantity == 0.0:
        # log(log.DEBUG, "Product code:[%s] has zero qty", code)
        return False
    product = Product.query.filter(Product.sku == code).first()
    if product:
        if name != product.title:
            product.title = name
            product.is_changed = True
        if category_path != product.category_path:
            product.category_path = category_path
            product.is_changed = True
        if price != product.price:
            product.price = price
            product.is_changed = True
        if quantity != product.qty:
            product.qty = quantity
            product.is_changed = True
        if product.is_deleted:
            product.is_changed = True
        product.updated = update_date
        product.is_deleted = False
        product.save()
    else:
        Product(
            sku=code,
            vidaxl_id=vidaxl_id,
            title=name,
            category_path=category_path,
            price=price,
            qty=quantity,
        ).save()
    return True


def upload_product(shop_id: int, limit=None):
    rows = Category.query.filter(Category.shop_id == shop_id).all()
    selected_categories = [r.path.split("/") for r in rows]

    def in_selected_category(category_path):
        path = category_path.split("/")
        for rule in selected_categories:
            rule_len = len(rule)
            if rule_len > len(path):
                continue
            if all(map(lambda x: x[0] == x[1], zip(rule, path[:rule_len]))):
                # this product in selected category
                return True
        return False

    shop = Shop.query.get(shop_id)
    log(log.INFO, "Update shop: %s", shop.name)
    begin_time = datetime.now()
    updated_product_count = 0
    # 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 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
    # memo-s2b-store.myshopify.com shop.primusmark.myshopify.com
    with shopify.Session.temp(
        shop.name, conf.VERSION_API, shop.private_app_access_token
    ):
        collection_names = {c.title: c.id for c in shopify.CustomCollection.find()}
        products = Product.query.filter(Product.is_new == True).all()  # noqa E712
        LEAVE_VIDAXL_PREFIX = Configuration.get_value(shop_id, "LEAVE_VIDAXL_PREFIX")
        for product in products:
            if in_selected_category(product.category_path):
                # check if product already created in the shop
                # ShopProduct.query.filter(ShopProduct.shop_id == shop_id).filter(ShopProduct.product_id)
                shop_products = [
                    sp for sp in product.shop_products if sp.shop_id == shop_id
                ]
                if not shop_products:
                    collection_name = product.category_path.split("/")[0]
                    log(
                        log.INFO,
                        "New product [%s] --> [%s]",
                        product.title,
                        collection_name,
                    )
                    if collection_name not in collection_names:
                        collection = shopify.CustomCollection.create(
                            dict(title=collection_name)
                        )
                        collection_names[collection_name] = collection.id
                    collection_id = collection_names[collection_name]

                    log(log.DEBUG, "price: %s", product.price)
                    title = product.title
                    if LEAVE_VIDAXL_PREFIX:
                        title = (
                            title.replace("vidaXL ", "")
                            if title.startswith("vidaXL ")
                            else title
                        )
                    price = get_price(product, shop_id)
                    description = scrap_description(product)
                    shop_prod = shopify.Product.create(
                        dict(
                            title=title,
                            body_html=description,
                            variants=[
                                dict(price=get_price(product, shop_id), sku=product.sku)
                            ],
                            images=[
                                {"src": img}
                                for img in scrap_img(product).get("images", [])
                            ],
                        )
                    )
                    assert shop_prod
                    ShopProduct(
                        shop_product_id=shop_prod.id,
                        shop_id=shop_id,
                        product_id=product.id,
                        price=price,
                    ).save()
                    collect = shopify.Collect.create(
                        dict(product_id=shop_prod.id, collection_id=collection_id)
                    )
                    assert collect
                    inventory_item_id = shop_prod.variants[0].inventory_item_id
                    inv_levels = shopify.InventoryLevel.find(
                        inventory_item_ids=inventory_item_id
                    )
                    if inv_levels:
                        items = shopify.InventoryItem.find(ids=inventory_item_id)
                        for item in items:
                            item.tracked = True
                            item.save()
                        for inv_level in inv_levels:
                            location_id = inv_level.location_id
                            inv_level.available = product.qty
                            shopify.InventoryLevel.set(
                                location_id, inventory_item_id, product.qty
                            )
                    product.is_new = False
                    product.save()
                    updated_product_count += 1
                    if limit is not None and updated_product_count >= limit:
                        return
    log(
        log.INFO,
        "Updated %d products in %d seconds",
        updated_product_count,
        (datetime.now() - begin_time).seconds,
    )
