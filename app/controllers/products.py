import tempfile
import csv
import hashlib
import json
import time
import xml.etree.ElementTree as ET
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


def download_vidaxl_product_from_xml(xml_url):
    log(log.INFO, "Download file: [%s]", xml_url)

    class NoNeedUpdate(Exception):
        pass

    def read_products_from_xml():

        with tempfile.NamedTemporaryFile(mode="w+") as file:
            # with open(xml_url, 'r') as file:
            hash_md5 = hashlib.md5()
            with requests.get(xml_url, stream=True) as r:
                r.raise_for_status()
                if r.encoding is None:
                    r.encoding = "windows-1252"
                for line in r.iter_lines():
                    hash_md5.update(line)
                    string_line = None
                    try:
                        string_line = line.decode()
                    except UnicodeDecodeError:
                        string_line = line.decode("windows-1252")
                    file.write(string_line)
                    file.write("\n")
            file.seek(0)
            file_hash = hash_md5.hexdigest()
            log(log.INFO, "CSV file hash: %s", file_hash)
            prev_check_sum = Configuration.get_common_value("CSV_CHECK_SUM")
            if prev_check_sum:
                log(log.INFO, "Previous hash: %s", prev_check_sum)
                if file_hash == prev_check_sum:
                    raise NoNeedUpdate()
            tree = ET.parse(file)
            try:
                for xml_prod in tree.findall('product'):
                    yield xml_prod
                Configuration.set_common_value("CSV_CHECK_SUM", file_hash)
            except requests.exceptions.ChunkedEncodingError as e:
                log(log.ERROR, "read_products_from_xml: [%s]", e)

    def get_images(prod):
        images = []
        for i in range(1, 13):
            if prod.find(f'Image_{i}').text:
                images.append(prod.find(f'Image_{i}').text)
        return images
    try:
        update_date = datetime.now()
        marked_to_delete_number = 0
        for i, xml_prod in enumerate(read_products_from_xml()):
            sku = xml_prod.find('SKU').text
            title = xml_prod.find('Title').text
            price = float(xml_prod.find('B2B_price').text)
            quantity = int(xml_prod.find('Stock').text)
            category_path = xml_prod.find('Category').text
            description = xml_prod.find('HTML_description').text
            if not xml_prod.find('EAN').text:
                ean = None
                vidaxl_id = None
            else:
                ean = int(xml_prod.find('EAN').text)
                vidaxl_id = int(xml_prod.find('EAN').text)
            path_ids = xml_prod.find('Category_id_path').text
            vendor = xml_prod.find('Brand').text
            images = get_images(xml_prod)
            prod = Product.query.filter(Product.sku == sku).first()
            if prod:
                if vendor != prod.vendor:
                    prod.vendor = vendor
                    prod.is_changed = True
                if quantity == 0 and prod.qty > 0:
                    prod.qty = quantity
                    prod.is_changed = True
                elif quantity > 0 and prod.qty == 0:
                    prod.qty = quantity
                    prod.is_changed = True
                if title != prod.title:
                    prod.title = title
                    prod.is_changed = True
                if category_path != prod.category_path:
                    prod.category_path = category_path
                    prod.is_changed = True
                if price != prod.price:
                    prod.price = price
                    prod.is_changed = True
                if prod.description != description:
                    prod.description = description
                    prod.is_changed = True
                if prod.ean != ean:
                    prod.ean = ean
                    prod.is_changed = True
                if prod.category_path_ids != path_ids:
                    prod.category_path_ids = path_ids
                    prod.is_changed = True

                if price == 0.0 and quantity == 0:
                    prod.deleted = True
                    prod.is_changed = True
                    marked_to_delete_number += 1

                prod.updated = update_date
                prod.save(False)

                if len(images) != len(prod.images):
                    # update images
                    Image.query.filter(Image.product_id == prod.id).delete()
                    for image in images:
                        Image(product_id=prod.id, url=image).save(False)
            else:
                product = Product(
                    vidaxl_id=vidaxl_id,
                    sku=sku,
                    title=title,
                    category_path=category_path,
                    price=price,
                    qty=quantity,
                    description=description,
                    ean=ean,
                    category_path_ids=path_ids,
                    vendor=vendor,
                ).save()
                for image in images:
                    Image(product_id=product.id, url=image).save(False)
            if not i % 1000:
                log(
                    log.DEBUG,
                    "download_vidaxl_product_from_xml: processed: %d items",
                    i,
                )
                db.session.commit()

        for product in (
            Product.query.filter(Product.updated < update_date)
            .filter(Product.is_deleted == False)  # noqa E712
            .all()
        ):
            product.qty = 0
            product.is_changed = True
            product.save()
        if marked_to_delete_number:
            log(
                log.INFO,
                "download_vidaxl_product_from_xml: %d products marked as deleted",
                marked_to_delete_number,
            )
        Configuration.set_common_value("LAST_VIDAXL_PROD_UPDATED", update_date)
    except NoNeedUpdate:
        log(log.INFO, "download_vidaxl_product_from_xml: No need update")
    finally:
        db.session.commit()


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
                    r.encoding = "windows-1252"
                for line in r.iter_lines():
                    hash_md5.update(line)
                    string_line = None
                    try:
                        string_line = line.decode()
                    except UnicodeDecodeError:
                        string_line = line.decode("windows-1252")
                    file.write(string_line)
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
            ean = int(csv_prod["EAN"]) if csv_prod["EAN"] else None
            path_ids = csv_prod["Category_id_path"]
            vendor = csv_prod["Brand"]
            images = [
                csv_prod[key]
                for key in csv_prod
                if key.startswith("Image ") and csv_prod[key] != ""
            ]
            # log(log.DEBUG, "Get images (%d)", len(images))
            vidaxl_id = int(csv_prod["EAN"])
            prod = Product.query.filter(Product.sku == sku).first()
            if prod:
                if vendor != prod.vendor:
                    prod.vendor = vendor
                    prod.is_changed = True
                if quantity == 0 and prod.qty > 0:
                    prod.qty = quantity
                    prod.is_changed = True
                elif quantity > 0 and prod.qty == 0:
                    prod.qty = quantity
                    prod.is_changed = True
                if title != prod.title:
                    prod.title = title
                    prod.is_changed = True
                if category_path != prod.category_path:
                    prod.category_path = category_path
                    prod.is_changed = True
                if price != prod.price:
                    prod.price = price
                    prod.is_changed = True
                if prod.description != description:
                    prod.description = description
                    prod.is_changed = True
                if prod.ean != ean:
                    prod.ean = ean
                    prod.is_changed = True
                if prod.category_path_ids != path_ids:
                    prod.category_path_ids = path_ids
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
                product = Product(
                    vidaxl_id=vidaxl_id,
                    sku=sku,
                    title=title,
                    category_path=category_path,
                    price=price,
                    qty=quantity,
                    description=description,
                    ean=ean,
                    category_path_ids=path_ids,
                    vendor=vendor,
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
            product.qty = 0
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
        download_vidaxl_product_from_xml(csv_url)
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


def get_all_collections():
    count = shopify.CustomCollection.count()
    collections = []
    if count > 0:
        page = shopify.CustomCollection.find()
        collections.extend(page)
        while page.has_next_page():
            page = page.next_page()
            collections.extend(page)
    log(log.INFO, "All collections: %s", collections)
    return collections


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
                            LEAVE_VIDAXL_PREFIX = Configuration.get_value(
                                shop.id,
                                "LEAVE_VIDAXL_PREFIX",
                                path=product.category_path,
                            )
                            log(
                                log.INFO,
                                "New product [%s]. Store: [%s]",
                                product.title,
                                shop,
                            )
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
                                    vendor=product.vendor,
                                    tags=product.tags,
                                    variants=[
                                        dict(
                                            price=price,
                                            sku=product.sku,
                                            barcode=product.ean,
                                        )
                                    ],
                                    images=images,
                                )
                            )
                            assert shop_prod
                            ShopProduct(
                                shop_product_id=shop_prod.id,
                                shop_id=shop.id,
                                product_id=product.id,
                                price=price,
                            ).save(False)
                            inventory_item_id = shop_prod.variants[0].inventory_item_id
                            inv_levels = shopify.InventoryLevel.find(
                                inventory_item_ids=inventory_item_id
                            )
                            if inv_levels:
                                items = shopify.InventoryItem.find(
                                    ids=inventory_item_id
                                )
                                for item in items:
                                    item.tracked = True
                                    item.cost = product.price
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
            if not updated_product_count % 100:
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
                                shop.id,
                                "LEAVE_VIDAXL_PREFIX",
                                path=product.category_path,
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
                                shopify_product.tags = product.tags
                                shopify_product.variants[0].price = price
                                shopify_product.variants[0].sku = product.sku
                                shopify_product.variants[0].barcode = product.ean
                                shopify_product.images = images
                                shopify_product.save()
                                inventory_item_id = shopify_product.variants[
                                    0
                                ].inventory_item_id
                                inv_levels = shopify.InventoryLevel.find(
                                    inventory_item_ids=inventory_item_id
                                )
                                if inv_levels:
                                    items = shopify.InventoryItem.find(
                                        ids=inventory_item_id
                                    )
                                    for item in items:
                                        item.tracked = True
                                        item.cost = product.price
                                        item.save()
                                    for inv_level in inv_levels:
                                        location_id = inv_level.location_id
                                        inv_level.available = product.qty
                                        shopify.InventoryLevel.set(
                                            location_id, inventory_item_id, product.qty
                                        )
                            except Exception:
                                shop_products[0].delete()
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
            if not updated_product_count % 100:
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
                        inventory_item_id = shopify_product.variants[
                            0
                        ].inventory_item_id
                        inv_levels = shopify.InventoryLevel.find(
                            inventory_item_ids=inventory_item_id
                        )
                        if inv_levels:
                            items = shopify.InventoryItem.find(ids=inventory_item_id)
                            for item in items:
                                item.cost = product.price
                                item.save()
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
                        shop_product.delete()
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
    try:
        for shop in Shop.query.all():
            log(log.INFO, "Upload products to stores by categories: %s", shop.name)
            begin_time = datetime.now()
            updated_product_count = 0
            with shopify.Session.temp(
                shop.name, conf.VERSION_API, shop.private_app_access_token
            ):
                products = Product.query.filter(
                    Product.is_deleted == False  # noqa E712
                ).all()
                total_products = len(products)
                for product in products:
                    if in_selected_category(shop, product.category_path):
                        shop_products = [
                            sp for sp in product.shop_products if sp.shop_id == shop.id
                        ]
                        if not shop_products:
                            LEAVE_VIDAXL_PREFIX = Configuration.get_value(
                                shop.id,
                                "LEAVE_VIDAXL_PREFIX",
                                path=product.category_path,
                            )
                            log(
                                log.INFO,
                                "New product [%s]. Store - [%s]",
                                product.title,
                                shop,
                            )
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
                                    vendor=product.vendor,
                                    tags=product.tags,
                                    variants=[
                                        dict(
                                            price=price,
                                            sku=product.sku,
                                            barcode=product.ean,
                                        )
                                    ],
                                    images=images,
                                )
                            )
                            assert shop_prod
                            ShopProduct(
                                shop_product_id=shop_prod.id,
                                shop_id=shop.id,
                                product_id=product.id,
                                price=price,
                            ).save(False)
                            inventory_item_id = shop_prod.variants[0].inventory_item_id
                            inv_levels = shopify.InventoryLevel.find(
                                inventory_item_ids=inventory_item_id
                            )
                            if inv_levels:
                                items = shopify.InventoryItem.find(
                                    ids=inventory_item_id
                                )
                                for item in items:
                                    item.tracked = True
                                    item.cost = product.price
                                    item.save()
                                for inv_level in inv_levels:
                                    location_id = inv_level.location_id
                                    inv_level.available = product.qty
                                    shopify.InventoryLevel.set(
                                        location_id, inventory_item_id, product.qty
                                    )
                    updated_product_count += 1
                    if not updated_product_count % 100:
                        log(
                            log.DEBUG,
                            "upload_products_to_store_by_category: processed: %d(%d) items",
                            updated_product_count,
                            total_products,
                        )
                        db.session.commit()
                    if limit is not None and updated_product_count >= limit:
                        break
        log(
            log.INFO,
            "Upload %d products in [%s] in %d seconds",
            updated_product_count,
            shop,
            (datetime.now() - begin_time).seconds,
        )
    finally:
        db.session.commit()


def change_vida_prefix_title(limit=None):  # 7
    """[Update products title in the stores]"""
    for shop in Shop.query.all():
        total_products = len(shop.products)
        log(log.INFO, "Update %d products title in shop: %s", total_products, shop.name)
        begin_time = datetime.now()
        updated_product_count = 0
        with shopify.Session.temp(
            shop.name, conf.VERSION_API, shop.private_app_access_token
        ):
            for shop_product in shop.products:
                product = shop_product.product
                if in_selected_category(shop, product.category_path):
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
                    if product.title != title:
                        try:
                            shopify_product = shopify.Product.find(
                                shop_product.shop_product_id
                            )
                            shopify_product.title = title
                            shopify_product.save()
                            product.title = title
                            product.save()
                        except Exception:
                            log(
                                log.ERROR,
                                "change_vida_prefix_title: Product %s not present in shop [%s]",
                                product,
                                shop,
                            )
                        log(
                            log.INFO,
                            "Product title %s was changed in [%s]",
                            shop_product,
                            shop,
                        )
                updated_product_count += 1
                if not updated_product_count % 100:
                    log(
                        log.DEBUG,
                        "change_vida_prefix_title: processed: %d(%d) items",
                        updated_product_count,
                        total_products,
                    )
                if limit is not None and updated_product_count >= limit:
                    break
        log(
            log.INFO,
            "Updated %d products in %s in %d seconds",
            updated_product_count,
            shop,
            (datetime.now() - begin_time).seconds,
        )


def set_b2b_price_in_shopify():  # CAUTION ! Not for use
    """[Update b2b price in the stores]"""
    for shop in Shop.query.all():
        log(log.INFO, "Update b2b price in shop: %s", shop.name)
        begin_time = datetime.now()
        updated_product_count = 0
        with shopify.Session.temp(
            shop.name, conf.VERSION_API, shop.private_app_access_token
        ):
            for shop_product in shop.products:
                product = shop_product.product
                try:
                    shopify_product = shopify.Product.find(shop_product.shop_product_id)
                    shopify_product.variants[0].cost = product.price
                    shopify_product.save()
                except Exception:
                    log(
                        log.ERROR,
                        "set_b2b_price_in_shopify: Product %s not present in shop [%s]",
                        product,
                        shop,
                    )
                log(
                    log.INFO,
                    "Product b2b price [%s] was changed in [%s]",
                    shop_product,
                    shop,
                )
            updated_product_count += 1
        log(
            log.INFO,
            "Updated %d products in %s in %d seconds",
            updated_product_count,
            shop,
            (datetime.now() - begin_time).seconds,
        )


def set_tags():  # CAUTION ! Not for use
    """[Update tags for product in the stores]"""
    for shop in Shop.query.all():
        log(log.INFO, "Update tags in shop: %s", shop.name)
        begin_time = datetime.now()
        updated_product_count = 0
        with shopify.Session.temp(
            shop.name, conf.VERSION_API, shop.private_app_access_token
        ):
            for shop_product in shop.products:
                product = shop_product.product
                try:
                    shopify_product = shopify.Product.find(shop_product.shop_product_id)
                    shopify_product.tags = product.tags
                    shopify_product.save()
                except Exception:
                    log(
                        log.ERROR,
                        "set_tags: Product %s not present in shop [%s]",
                        product,
                        shop,
                    )
                log(
                    log.INFO,
                    "Product tags [%s] was changed in [%s]",
                    shop_product,
                    shop,
                )
            updated_product_count += 1
        log(
            log.INFO,
            "Updated %d products in %s in %d seconds",
            updated_product_count,
            shop,
            (datetime.now() - begin_time).seconds,
        )


def set_vendor_and_qty():  # CAUTION ! Not for use
    """[Update vendor and qty for product in the stores]"""
    for shop in Shop.query.all():
        log(log.INFO, "Update vendor and qty in shop: %s", shop.name)
        begin_time = datetime.now()
        updated_product_count = 0
        with shopify.Session.temp(
            shop.name, conf.VERSION_API, shop.private_app_access_token
        ):
            for shop_product in shop.products:
                product = shop_product.product
                try:
                    price = get_price(product, shop.id)
                    shopify_product = shopify.Product.find(shop_product.shop_product_id)
                    shopify_product.vendor = product.vendor
                    shopify_product.variants[0].price = price
                    shopify_product.variants[0].inventory_management = "shopify"
                    shopify_product.variants[0].inventory_quantity = int(product.qty)
                    inventory_item_id = shopify_product.variants[0].inventory_item_id
                    inv_levels = shopify.InventoryLevel.find(
                        inventory_item_ids=inventory_item_id
                    )
                    inv_levels[0].available = product.qty
                    shopify_product.save()
                    shop_product.price = price
                    shop_product.save()
                    if inv_levels:
                        items = shopify.InventoryItem.find(ids=inventory_item_id)
                        for item in items:
                            item.tracked = True
                            item.cost = product.price
                            item.save()
                        for inv_level in inv_levels:
                            location_id = inv_level.location_id
                            shopify.InventoryLevel.set(
                                location_id, inventory_item_id, product.qty
                            )
                    time.sleep(1)
                except Exception:
                    log(
                        log.ERROR,
                        "set_vendor_and_qty: Product %s not present in shop [%s]",
                        product,
                        shop,
                    )
                log(
                    log.INFO,
                    "Product vendor and qty [%s] was changed in [%s]",
                    shop_product,
                    shop,
                )
            updated_product_count += 1
        log(
            log.INFO,
            "Updated %d products in %s in %d seconds",
            updated_product_count,
            shop,
            (datetime.now() - begin_time).seconds,
        )


def set_categories():  # CAUTION ! Not for use
    """[Update product category in the stores]"""
    for shop in Shop.query.all():
        log(log.INFO, "Update categories in shop: %s", shop.name)
        begin_time = datetime.now()
        updated_product_count = 0
        with shopify.Session.temp(
            shop.name, conf.VERSION_API, shop.private_app_access_token
        ):
            collection_names = {c.title: c.id for c in get_all_collections()}
            for shop_product in shop.products:
                product = shop_product.product
                collection_name = product.category_path.split(CATEGORY_SPLITTER)[-1]
                if collection_name not in collection_names:
                    collection = shopify.CustomCollection.create(
                        dict(title=collection_name)
                    )
                    collection_names[collection_name] = collection.id
                collection_id = collection_names[collection_name]
                try:
                    shopify.Collect.create(
                        dict(product_id=shop_product.id, collection_id=collection_id)
                    )
                except Exception:
                    log(
                        log.ERROR,
                        "set_categories: Product %s not present in shop [%s]",
                        product,
                        shop,
                    )
                log(
                    log.INFO,
                    "Product categories [%s] was changed in [%s]",
                    shop_product,
                    shop,
                )
            updated_product_count += 1
        log(
            log.INFO,
            "Updated %d products in %s in %d seconds",
            updated_product_count,
            shop,
            (datetime.now() - begin_time).seconds,
        )


def custom_update():  # CAUTION ! Not for use
    """[Update product category, set tags, set barcode]"""

    class ProcessedId(object):
        FILE_PATH = "custom_update_ids.json"

        def __init__(self):
            self.ids = []
            self._read_from_file()

        def _read_from_file(self):
            try:
                with open(ProcessedId.FILE_PATH, "r") as file:
                    self.ids = json.load(file)
            except FileNotFoundError:
                pass

        def _save(self):
            with open(ProcessedId.FILE_PATH, "w") as file:
                json.dump(self.ids, file, indent=2)

        def add_id(self, id):
            self.ids += [id]
            self._save()

        def is_done(self, id):
            return id in self.ids

    processed_ids = ProcessedId()

    for shop in Shop.query.all():
        log(log.INFO, "Custom update in shop: %s", shop.name)
        begin_time = datetime.now()
        updated_product_count = 0
        with shopify.Session.temp(
            shop.name, conf.VERSION_API, shop.private_app_access_token
        ):
            collection_names = {c.title: c.id for c in get_all_collections()}
            for shop_product in shop.products:
                if processed_ids.is_done(shop_product.id):
                    continue
                time.sleep(2)
                product = shop_product.product
                collection_name = product.category_path.split(CATEGORY_SPLITTER)[-1]
                try:
                    if collection_name not in collection_names:
                        collection = shopify.CustomCollection.create(
                            dict(title=collection_name)
                        )
                        collection_names[collection_name] = collection.id
                    collection_id = collection_names[collection_name]
                    shopify_product = shopify.Product.find(shop_product.shop_product_id)
                    shopify_product.tags = product.tags
                    shopify_product.variants[0].barcode = product.ean
                    shopify_product.save()
                    shopify.Collect.create(
                        dict(
                            product_id=shop_product.shop_product_id,
                            collection_id=collection_id,
                        )
                    )
                    processed_ids.add_id(shop_product.id)
                except Exception:
                    log(
                        log.ERROR,
                        "custom_update: Product %s not present in shop [%s]",
                        product,
                        shop,
                    )
                log(
                    log.INFO,
                    "Data [%s] was changed in [%s]",
                    shop_product,
                    shop,
                )

            updated_product_count += 1
        log(
            log.INFO,
            "Updated %d products in %s in %d seconds",
            updated_product_count,
            shop,
            (datetime.now() - begin_time).seconds,
        )
