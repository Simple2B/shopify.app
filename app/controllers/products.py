import tempfile
import csv
import hashlib
from datetime import datetime
import requests
import shopify
from app.models import (
    Configuration,
    Product,
    Shop,
    ShopProduct,
    Image,
)
from app import db
from .price import get_price
from .scrap import scrap_img, scrap_description
from app.logger import log
from app.vida_xl import VidaXl
from config import BaseConfig as conf

NO_PHOTO_IMG = f"https://{conf.HOST_NAME}/static/images/no-photo-polycar-300x210.png"
CATEGORY_SPLITTER = conf.CATEGORY_SPLITTER


def download_vidaxl_product_from_csv(csv_url, limit=None):
    log(log.INFO, "Download file: [%s]", csv_url)

    class NoNeedUpdate(Exception):
        pass

    def read_products_from_csv():

        with tempfile.NamedTemporaryFile(mode="w+") as file:
            hash_md5 = hashlib.md5()
            with requests.get(csv_url, stream=True) as r:
                r.raise_for_status()
                if r.encoding is None:
                    r.encoding = "utf-8"
                for line in r.iter_lines(decode_unicode=True):
                    hash_md5.update(line.encode())
                    file.write(line)
                    file.write("\n")

            # r = requests.get(csv_url, stream=True)
            # if r.encoding is None:
            #     r.encoding = 'utf-8'
            file.seek(0)
            file_hash = hash_md5.hexdigest()
            log(log.INFO, "CSV file hash: %s", file_hash)
            prev_check_sum = Configuration.get_common_value("CSV_CHECK_SUM")
            if prev_check_sum:
                log(log.INFO, "Previous hash: %s", prev_check_sum)
                if file_hash == prev_check_sum:
                    raise NoNeedUpdate()
            if limit is not None:
                row_count = 0
            csv_reader = csv.reader(file)
            keys = []
            try:
                for row in csv_reader:
                    if not keys:
                        keys = row
                    else:
                        csv_prod = {i[0]: i[1] for i in zip(keys, row)}
                        yield csv_prod
                        if limit is not None:
                            row_count += 1
                            if row_count >= limit:
                                break
                Configuration.set_common_value("CSV_CHECK_SUM", file_hash)
            except requests.exceptions.ChunkedEncodingError as e:
                log(log.ERROR, "read_products_from_csv: [%s]", e)

    try:
        update_date = datetime.now()
        for i, csv_prod in enumerate(read_products_from_csv()):
            sku = csv_prod["SKU"]
            title = csv_prod["Product_title"]
            price = float(csv_prod["B2B price"])
            quantity = float(csv_prod["Stock"])
            category_path = csv_prod["Category"]
            description = csv_prod["HTML_description"]
            images = [
                csv_prod[key]
                for key in csv_prod
                if key.startswith("Image ") and csv_prod[key] != ""
            ]
            # log(log.DEBUG, "Get images (%d)", len(images))
            vidaxl_id = int(csv_prod["EAN"])
            prod = Product.query.filter(Product.sku == sku).first()
            if prod:
                if quantity <= 0:
                    if not prod.is_deleted:
                        # delete product
                        prod.is_deleted = True
                        prod.is_changed = True
                        prod.save(False)
                else:
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
                    if prod.description != description:
                        prod.description = description
                        prod.is_changed = True

                    if prod.is_deleted:
                        prod.is_deleted = False
                        prod.is_changed = True

                    prod.updated = update_date
                    prod.save(False)

                    if len(images) != len(prod.images):
                        # update images
                        Image.query.filter(Image.product_id == prod.id).delete()
                        for image in images:
                            Image(product_id=prod.id, url=image).save(False)
            else:
                if quantity > 0:
                    product = Product(
                        vidaxl_id=vidaxl_id,
                        sku=sku,
                        title=title,
                        category_path=category_path,
                        price=price,
                        qty=quantity,
                        description=description,
                    ).save()
                    for image in images:
                        Image(product_id=product.id, url=image).save(False)

            if not i % 1000:
                log(
                    log.DEBUG,
                    "download_vidaxl_product_from_csv: processed: %d items",
                    i,
                )
                db.session.commit()
        marked_to_delete_number = 0
        for product in (
            Product.query.filter(Product.updated < update_date)
            .filter(Product.is_deleted == False)  # noqa E712
            .all()
        ):
            product.is_deleted = True
            product.is_changed = True
            product.save()
            marked_to_delete_number += 1
        if marked_to_delete_number:
            log(
                log.INFO,
                "download_vidaxl_product_from_csv: %d products marked as deleted",
                marked_to_delete_number,
            )
        Configuration.set_common_value("LAST_VIDAXL_PROD_UPDATED", update_date)
    except NoNeedUpdate:
        log(log.INFO, "download_vidaxl_product_from_csv: No need update")
    finally:
        db.session.commit()


def download_vidaxl_product_by_api(limit=None):
    vida = VidaXl()
    update_date = datetime.now()
    log(log.INFO, "Start update VidaXl products")
    updated_product_count = 0
    for prod in vida.products:
        # add product into DB
        if not update_product_db(prod, update_date):
            continue
        if not updated_product_count % 1000:
            db.session.commit()
        updated_product_count += 1
    db.session.commit()
    for product in (
        Product.query.filter(Product.updated < update_date)
        .filter(Product.is_deleted == False)  # noqa E712
        .all()
    ):
        product.is_deleted = True
        product.is_changed = True
        product.save()
    log(
        log.INFO,
        "Updated %d products in %d seconds",
        updated_product_count,
        (datetime.now() - update_date).seconds,
    )


def download_products(limit=None):
    csv_url = Configuration.get_value(1, "CSV_URL", path="/")
    if csv_url:
        download_vidaxl_product_from_csv(csv_url, limit)
    else:
        download_vidaxl_product_by_api(limit)


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
        product = Product.query.filter(Product.sku == code).first()
        if product:
            product.is_deleted = True
            product.is_changed = True
            product.save(False)
            log(log.DEBUG, "Product code:[%s] deleted...", product.sku)
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
        product.save(False)
    else:
        Product(
            sku=code,
            vidaxl_id=vidaxl_id,
            title=name,
            category_path=category_path,
            price=price,
            qty=quantity,
        ).save(False)
    return True


def in_selected_category(shop, category_path):
    selected_categories = [r.path.split(CATEGORY_SPLITTER) for r in shop.categories]
    path = category_path.split(CATEGORY_SPLITTER)
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
    total_products = len(products)
    try:
        for product in products:
            for shop in Shop.query.all():
                if in_selected_category(shop, product.category_path):
                    with shopify.Session.temp(
                        shop.name, conf.VERSION_API, shop.private_app_access_token
                    ):
                        shop_products = [
                            sp for sp in product.shop_products if sp.shop_id == shop.id
                        ]
                        if not shop_products:
                            collection_names = {
                                c.title: c.id for c in shopify.CustomCollection.find()
                            }
                            LEAVE_VIDAXL_PREFIX = Configuration.get_value(
                                shop.id, "LEAVE_VIDAXL_PREFIX", path=product.category_path
                            )
                            collection_name = product.category_path.split(
                                CATEGORY_SPLITTER
                            )[0]
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
                            if not LEAVE_VIDAXL_PREFIX:
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
                                images = [{"src": NO_PHOTO_IMG}]
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
            product.save(False)
            updated_product_count += 1
            if not updated_product_count % 1000:
                log(
                    log.DEBUG,
                    "upload_new_products_vidaxl_to_store: processed: %d(%d) items",
                    updated_product_count,
                    total_products,
                )
                db.session.commit()
            if limit is not None and updated_product_count >= limit:
                break
    finally:
        db.session.commit()
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
        Product.query.filter(Product.is_changed == True)  # noqa E712
        .filter(Product.is_deleted == False)  # noqa E712
        .all()
    )
    updated_product_count = 0
    total_products = len(products)
    try:
        for product in products:
            for shop in Shop.query.all():
                if in_selected_category(shop, product.category_path):
                    with shopify.Session.temp(
                        shop.name, conf.VERSION_API, shop.private_app_access_token
                    ):
                        shop_products = [
                            sp for sp in product.shop_products if sp.shop_id == shop.id
                        ]
                        if shop_products:
                            LEAVE_VIDAXL_PREFIX = Configuration.get_value(
                                shop.id, "LEAVE_VIDAXL_PREFIX", path=product.category_path
                            )
                            title = product.title
                            if not LEAVE_VIDAXL_PREFIX:
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
                                images = [{"src": NO_PHOTO_IMG}]
                            else:
                                images = [{"src": img} for img in images]
                            price = get_price(product, shop.id)
                            try:
                                shopify_product = shopify.Product.find(
                                    shop_products[0].shop_product_id
                                )
                                shopify_product.title = title
                                shopify_product.body_html = description
                                shopify_product.variants[0].price = price
                                shopify_product.variants[0].sku = product.sku
                                shopify_product.images = images
                                shopify_product.save()
                            except Exception:
                                log(
                                    log.ERROR,
                                    "update_products_vidaxl_to_store: Product %s not present in shop [%s]",
                                    product,
                                    shop,
                                )
                            log(
                                log.INFO,
                                "Product %s was updated in %s",
                                product,
                                shop,
                            )
            product.is_changed = False
            product.save(False)
            updated_product_count += 1
            if not updated_product_count % 1000:
                log(
                    log.DEBUG,
                    "update_products_vidaxl_to_store: processed: %d(%d) items",
                    updated_product_count,
                    total_products,
                )
                db.session.commit()
            if limit is not None and updated_product_count >= limit:
                break
    finally:
        db.session.commit()
    log(
        log.INFO,
        "Updated %d products in %d seconds",
        updated_product_count,
        (datetime.now() - begin_time).seconds,
    )


def delete_vidaxl_product_from_store(limit=None):  # 3
    """[Delete VidaXL product from stores]"""
    begin_time = datetime.now()
    # TODO: consider select from shop_products
    products = (
        Product.query.filter(Product.is_changed == True)  # noqa E712
        .filter(Product.is_deleted == True)  # noqa E712
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
                    for prod in shop_products:
                        try:
                            shopify_product = shopify.Product.find(prod.shop_product_id)
                            shopify_product.destroy()
                        except Exception:
                            pass
                        prod.delete()

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
            for shop_product in shop.products:
                product = shop_product.product
                price = get_price(product, shop.id)
                if abs(price - shop_product.price) > 0.0001:
                    try:
                        shopify_product = shopify.Product.find(
                            shop_product.shop_product_id
                        )
                        shopify_product.variants[0].price = price
                        shopify_product.save()
                        shop_product.price = price
                        shop_product.save()
                    except Exception:
                        log(
                            log.ERROR,
                            "change_product_price: Product %s not present in shop [%s]",
                            product,
                            shop,
                        )
                    log(
                        log.INFO,
                        "Product price [%f] %s was changed in [%s]",
                        price,
                        shop_product,
                        shop,
                    )
                updated_product_count += 1
                if limit is not None and updated_product_count >= limit:
                    break
        log(
            log.INFO,
            "Updated %d products in %s in %d seconds",
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
            for shop_product in shop.products:
                product = shop_product.product
                if not in_selected_category(shop, product.category_path):
                    # this product need remove from the shop
                    try:
                        shopify_product = shopify.Product.find(
                            shop_product.shop_product_id
                        )
                        shopify_product.destroy()
                        shop_product.delete()
                        log(log.INFO, "%s was deleted from [%s]", product, shop)
                    except Exception:
                        log(log.ERROR, "%s *NOT IN* [%s]", product, shop)
                    deleted_product_count += 1
                    if limit is not None and deleted_product_count >= limit:
                        break
        log(
            log.INFO,
            "Deleted %d products in %s in %d seconds",
            deleted_product_count,
            shop,
            (datetime.now() - begin_time).seconds,
        )


def upload_products_to_store_by_category(limit=None):  # 6
    """Upload products to stores by categories"""
    for shop in Shop.query.all():
        log(log.INFO, "Upload products to stores by categories: %s", shop.name)
        begin_time = datetime.now()
        updated_product_count = 0
        with shopify.Session.temp(
            shop.name, conf.VERSION_API, shop.private_app_access_token
        ):
            custom_collections = shopify.CustomCollection.find()
            assert custom_collections
            collection_names = {c.title: c.id for c in custom_collections}
            products = Product.query.filter(
                Product.is_deleted == False  # noqa E712
            ).all()
            for product in products:
                if in_selected_category(shop, product.category_path):
                    shop_products = [
                        sp for sp in product.shop_products if sp.shop_id == shop.id
                    ]
                    if not shop_products:
                        LEAVE_VIDAXL_PREFIX = Configuration.get_value(
                            shop.id, "LEAVE_VIDAXL_PREFIX", path=product.category_path
                        )
                        collection_name = product.category_path.split(
                            CATEGORY_SPLITTER
                        )[0]
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
                        if not LEAVE_VIDAXL_PREFIX:
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
                            images = [{"src": NO_PHOTO_IMG}]
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
                            break
        log(
            log.INFO,
            "Upload %d products in [%s] in %d seconds",
            updated_product_count,
            shop,
            (datetime.now() - begin_time).seconds,
        )
