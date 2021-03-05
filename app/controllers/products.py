from datetime import datetime

import shopify
from app.models import Configuration, Category, Product, Shop, ShopProduct
from .price import get_price
from .scrap import scrap_img
from app.logger import log
from app.vida_xl import VidaXl
from app import db
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


def download_products(limit=None):
    vida = VidaXl()
    update_date = datetime.now()
    log(log.INFO, "Start update VidaXl products - %s", "All" if not limit else limit)
    updated_product_count = 0
    for prod in vida.products:
        # add product into DB
        if not update_product_db(prod, update_date, updated_product_count):
            continue
        updated_product_count += 1
        if limit is not None and updated_product_count >= limit:
            break
    db.session.commit()
    for product in (
        Product.query.filter(Product.updated < update_date)
        .filter(Product.is_deleted == False)  # noqa E712
        .all()
    ):
        product.is_deleted = True
        product.is_changed = True
        product.save(False)
        log(log.DEBUG, "Product code:[%s] deleted...", product.sku)
    db.session.commit()
    log(
        log.INFO,
        "Updated %d products in %d seconds",
        updated_product_count,
        (datetime.now() - update_date).seconds,
    )


def update_product_db(prod, update_date=None, updated_product_count=None):
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
        if updated_product_count:
            product.save(updated_product_count % 100 == 0)
        else:
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


def upload_product(shop_id: int):
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
                    shop_prod = shopify.Product.create(
                        dict(
                            title=title,
                            variants=[
                                dict(price=get_price(product, shop_id), sku=product.sku)
                            ],
                            images=[
                                {"src": img}
                                for img in scrap_img(product.vidaxl_id).get(
                                    "images", []
                                )
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
    log(
        log.INFO,
        "Updated %d products in %d seconds",
        updated_product_count,
        (datetime.now() - begin_time).seconds,
    )
