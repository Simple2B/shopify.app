from datetime import datetime

from app.models import Configuration
from app.controllers import scrap_img
from app.logger import log
from app.vida_xl import VidaXl
from app.models import Product
from app import db


def upload_product(
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
    updated_product_count = 0
    for prod in vida.products:
        # add product into DB
        name = prod["name"]
        code = prod["code"]
        price = float(prod["price"])
        quantity = float(prod["quantity"])
        currency = prod["currency"]
        if currency != "EUR":
            log(
                log.WARNING,
                "Product code: [%s] skipped - currency: [%s]",
                code,
                currency,
            )
            continue
        category_path = prod["category_path"]
        if quantity == 0.0:
            # log(log.DEBUG, "Product code:[%s] has zero qty", code)
            continue
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
            product.updated = update_date
            product.save(updated_product_count % 100 == 0)
        else:
            Product(
                sku=code,
                title=name,
                category_path=category_path,
                price=price,
                qty=quantity,
            ).save()
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
