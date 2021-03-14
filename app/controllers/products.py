from datetime import datetime
import shopify
from flask import url_for
from app.models import Configuration, Product, Shop, ShopProduct
from .price import get_price
from .scrap import scrap_img, scrap_description
from app.logger import log
from app.vida_xl import VidaXl
from config import BaseConfig as conf


def download_products(limit=None):
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


def in_selected_category(shop, category_path):
    selected_categories = [r.path.split("/") for r in shop.categories]
    path = category_path.split("/")
    for rule in selected_categories:
        rule_len = len(rule)
        if rule_len > len(path):
            continue
        if all(map(lambda x: x[0] == x[1], zip(rule, path[:rule_len]))):
            # this product in selected category
            return True
    return False


def upload_new_products_vidaxl_to_store(limit=None):  # 1
    """Upload new products from VidaXL to stores by categories"""
    begin_time = datetime.now()
    products = Product.query.filter(Product.is_new == True).all()  # noqa E712
    updated_product_count = 0
    for product in products:
        for shop in Shop.query.all():
            with shopify.Session.temp(
                shop.name, conf.VERSION_API, shop.private_app_access_token
            ):
                if in_selected_category(shop, product.category_path):
                    shop_products = [
                        sp for sp in product.shop_products if sp.shop_id == shop.id
                    ]
                    if not shop_products:
                        collection_names = {
                            c.title: c.id for c in shopify.CustomCollection.find()
                        }
                        LEAVE_VIDAXL_PREFIX = Configuration.get_value(
                            shop.id, "LEAVE_VIDAXL_PREFIX"
                        )
                        collection_name = product.category_path.split("/")[0]
                        log(
                            log.INFO,
                            "New product [%s] --> [%s]. Store: [%s]",
                            product.title,
                            collection_name,
                            shop,
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
                        price = get_price(product, shop.id)
                        description = scrap_description(product)
                        if not description:
                            description = "<p>No description</p>"
                        images = scrap_img(product)
                        if not images:
                            images = [
                                {
                                    "src": url_for('static', filename='images/no-photo-polycar-300x210.png')

                                }  # noqa E712
                            ]
                        else:
                            images = [{"src": img} for img in images]
                        shop_prod = shopify.Product.create(
                            dict(
                                title=title,
                                body_html=description,
                                variants=[dict(price=price, sku=product.sku)],
                                images=images,
                            )
                        )
                        assert shop_prod
                        ShopProduct(
                            shop_product_id=shop_prod.id,
                            shop_id=shop.id,
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
                        log(
                            log.INFO,
                            "Product %s was uploaded in %s",
                            product,
                            shop,
                        )
        product.is_new = False
        product.is_changed = False
        product.save()
        updated_product_count += 1
        if limit is not None and updated_product_count >= limit:
            return
    log(
        log.INFO,
        "Upload %d new products in %d seconds",
        updated_product_count,
        (datetime.now() - begin_time).seconds,
    )


def update_products_vidaxl_to_store(limit=None):  # 2
    """[Update VidaXL products in the stores]"""
    begin_time = datetime.now()
    products = (
        Product.query.filter(Product.is_changed == True)
        .filter(Product.is_deleted == False)
        .all()
    )
    updated_product_count = 0
    for product in products:
        for shop in Shop.query.all():
            with shopify.Session.temp(
                shop.name, conf.VERSION_API, shop.private_app_access_token
            ):
                if in_selected_category(shop, product.category_path):
                    shop_products = [
                        sp for sp in product.shop_products if sp.shop_id == shop.id
                    ]
                    if shop_products:
                        LEAVE_VIDAXL_PREFIX = Configuration.get_value(
                            shop.id, "LEAVE_VIDAXL_PREFIX"
                        )
                        title = product.title
                        if LEAVE_VIDAXL_PREFIX:
                            title = (
                                title.replace("vidaXL ", "")
                                if title.startswith("vidaXL ")
                                else title
                            )
                        description = scrap_description(product)
                        if not description:
                            description = "<p>No description</p>"
                        images = scrap_img(product)
                        if not images:
                            images = [
                                {
                                    "src": url_for('static', filename='images/no-photo-polycar-300x210.png')
                                }  # noqa E712
                            ]
                        else:
                            images = [{"src": img} for img in images]
                        price = get_price(product, shop.id)
                        shopify_product = shopify.Product.find(
                            shop_products[0].shop_product_id
                        )
                        shopify_product.title = title
                        shopify_product.body_html = description
                        shopify_product.variants[0].price = price
                        shopify_product.variants[0].sku = product.sku
                        shopify_product.images = images
                        shopify_product.save()
                        log(
                            log.INFO,
                            "Product %s was updated in %s",
                            product,
                            shop,
                        )
        product.is_changed = False
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


def delete_vidaxl_product_from_store(limit=None):  # 3
    """[Delete VidaXL product from stores]"""
    begin_time = datetime.now()
    products = (
        Product.query.filter(Product.is_changed == True)
        .filter(Product.is_deleted == True)
        .all()
    )
    deleted_product_count = 0
    for product in products:
        for shop in Shop.query.all():
            with shopify.Session.temp(
                shop.name, conf.VERSION_API, shop.private_app_access_token
            ):
                if in_selected_category(shop, product.category_path):
                    shop_products = [
                        sp for sp in product.shop_products if sp.shop_id == shop.id
                    ]
                    if shop_products:
                        shopify_product = shopify.Product.find(
                            shop_products[0].shop_product_id
                        )
                        shopify_product.destroy()
                        shop_products[0].delete()
                        log(
                            log.INFO,
                            "Product %s was deleted in %s",
                            product,
                            shop,
                        )
                        deleted_product_count += 1
        product.is_changed = False
        product.save()
        if limit is not None and deleted_product_count >= limit:
            return
    log(
        log.INFO,
        "Deleted %d products in %d seconds",
        deleted_product_count,
        (datetime.now() - begin_time).seconds,
    )


def change_product_price(limit=None):  # 4
    """[Update products price in the stores]"""
    for shop in Shop.query.all():
        log(log.INFO, "Update products price in shop: %s", shop.name)
        begin_time = datetime.now()
        updated_product_count = 0
        with shopify.Session.temp(
            shop.name, conf.VERSION_API, shop.private_app_access_token
        ):
            if shop.products:
                for shop_product in shop.products:
                    product = shop_product.product
                    price = get_price(product, shop.id)
                    if price != shop_product.price:
                        shopify_product = shopify.Product.find(
                            shop_product.shop_product_id
                        )
                        shopify_product.variants[0].price = price
                        shopify_product.save()
                        log(
                            log.INFO,
                            "Product price [%d] %s was changed in %s",
                            price,
                            shop_product,
                            shop,
                        )
                        updated_product_count += 1
                        if limit is not None and updated_product_count >= limit:
                            return
        log(
            log.INFO,
            "Updated price %f products in %s in %d seconds",
            updated_product_count,
            shop,
            (datetime.now() - begin_time).seconds,
        )


def delete_products_from_store_exclude_category(limit=None):  # 5
    """[Delete products from store exclude chosen category]"""
    for shop in Shop.query.all():
        log(log.INFO, "Delete products exclude category in shop: %s", shop.name)
        begin_time = datetime.now()
        deleted_product_count = 0
        with shopify.Session.temp(
            shop.name, conf.VERSION_API, shop.private_app_access_token
        ):
            if shop.products:
                for shop_product in shop.products:
                    product = shop_product.product
                    if not in_selected_category(shop, product.category_path):
                        try:
                            shopify_product = shopify.Product.find(
                                shop_product.shop_product_id
                            )
                            shopify_product.destroy()
                            shop_product.delete()
                            shop_product.save()
                            deleted_product_count += 1
                            log(log.INFO, "%s was deleted from %s", product, shop)
                        except Exception:
                            log(log.ERROR, "%s *NOT IN* %s", product, shop)
                        if limit is not None and deleted_product_count >= limit:
                            return
        log(
            log.INFO,
            "Deleted %d products in %s in %d seconds",
            deleted_product_count,
            shop,
            (datetime.now() - begin_time).seconds,
        )


def upload_products_to_store_by_category(limit=None):  # 6
    """[Upload products to stores by categories]"""
    for shop in Shop.query.all():
        log(log.INFO, "Upload products to stores by categories: %s", shop.name)
        begin_time = datetime.now()
        updated_product_count = 0
        with shopify.Session.temp(
            shop.name, conf.VERSION_API, shop.private_app_access_token
        ):
            products = Product.query.filter(Product.is_deleted == False).all()
            for product in products:
                if in_selected_category(shop, product.category_path):
                    shop_products = [
                        sp for sp in product.shop_products if sp.shop_id == shop.id
                    ]
                    if not shop_products:
                        LEAVE_VIDAXL_PREFIX = Configuration.get_value(
                            shop.id, "LEAVE_VIDAXL_PREFIX"
                        )
                        collection_names = {
                            c.title: c.id for c in shopify.CustomCollection.find()
                        }
                        collection_name = product.category_path.split("/")[0]
                        log(
                            log.INFO,
                            "New product [%s] --> [%s]. Store - [%s]",
                            product.title,
                            collection_name,
                            shop,
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
                        price = get_price(product, shop.id)
                        description = scrap_description(product)
                        if not description:
                            description = "<p>No description</p>"
                        images = scrap_img(product)
                        if not images:
                            images = [
                                {
                                    "src": url_for('static', filename='images/no-photo-polycar-300x210.png')
                                }  # noqa E712
                            ]
                        else:
                            images = [{"src": img} for img in images]
                        shop_prod = shopify.Product.create(
                            dict(
                                title=title,
                                body_html=description,
                                variants=[dict(price=price, sku=product.sku)],
                                images=images,
                            )
                        )
                        assert shop_prod
                        ShopProduct(
                            shop_product_id=shop_prod.id,
                            shop_id=shop.id,
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
                        updated_product_count += 1
                        if limit is not None and updated_product_count >= limit:
                            return
        log(
            log.INFO,
            "Upload %d products in %s in %d seconds",
            updated_product_count,
            shop,
            (datetime.now() - begin_time).seconds,
        )
