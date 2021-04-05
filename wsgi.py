#!/user/bin/env python
import os
import click

from app import create_app, db, models, forms
from app.logger import log

app = create_app()


def process_exists(pid: int):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


# flask cli context setup
@app.shell_context_processor
def get_context():
    """Objects exposed here will be automatically available from the shell."""
    return dict(app=app, db=db, m=models, forms=forms)


@app.cli.command()
def create_db():
    """Create new database."""
    db.create_all()


@app.cli.command()
@click.confirmation_option(prompt="Drop all database tables?")
def drop_db():
    """Drop database."""
    db.drop_all()


@app.cli.command()
def scrappy():
    """Test scrap images from VidaXL"""
    # db.drop_all()
    from app.controllers import scrap

    scrap.scrappy_all_products(40)


@app.cli.command()
def update_2b2_price():
    """Update b2b price"""
    from app.controllers import set_b2b_price_in_shopify
    set_b2b_price_in_shopify()


@app.cli.command()
def update_tags():
    """Updating shop product's tags only"""
    from app.controllers import set_tags
    set_tags()


@app.cli.command()
@click.option("--limit", default=0, help="Number of products.")
def update(limit):
    """Update ALL"""
    import getpass
    from datetime import datetime
    begin = datetime.now()
    FILE_NAME = f"/tmp/UPDATING_{getpass.getuser()}"
    try:
        with open(FILE_NAME, "r") as f:
            pid = int(f.readline())
            if process_exists(pid):
                # log(log.WARNING, "Updating in progress...")
                return
    except IOError:
        pass

    with open(FILE_NAME, "w") as f:
        f.write(f"{os.getpid()}\n")
    log(log.INFO, "---==START UPDATE==---")
    _update_vidaxl_products()
    _update_shop_products(limit)
    log(log.INFO, "---==FINISH UPDATE==---")
    os.remove(FILE_NAME)
    log(log.INFO, "Updated in %d seconds", (datetime.now() - begin).seconds)


@app.cli.command()
# @click.option("--limit", default=0, help="Number of products.")
def update_vidaxl_products():
    """Update all products from VidaXl"""
    _update_vidaxl_products()


def _update_vidaxl_products():
    from app.controllers import download_products
    download_products()


@app.cli.command()
@click.argument("sku")
def vida_product(sku):
    """Get VidaXl product by SKU"""
    import json
    from app.vida_xl import VidaXl

    print(json.dumps(VidaXl().get_product(sku), indent=2))


@app.cli.command()
@click.option("--limit", default=0, help="Max. Number of products for update.")
def update_shop_products(limit):
    _update_shop_products(limit)


def _update_shop_products(limit):
    """Upload all products to Shop(s)"""
    from app.controllers import (
        upload_new_products_vidaxl_to_store,
        upload_products_to_store_by_category,
        update_products_vidaxl_to_store,
        change_product_price,
        delete_products_from_store_exclude_category,
        delete_vidaxl_product_from_store,
        change_vida_prefix_title
    )
    limit = limit if limit else None
    delete_products_from_store_exclude_category(limit)
    delete_vidaxl_product_from_store(limit)

    upload_products_to_store_by_category(limit)
    update_products_vidaxl_to_store(limit)

    change_product_price(limit)
    change_vida_prefix_title(limit)
    upload_new_products_vidaxl_to_store(limit)


@app.cli.command()
@click.option("--limit", default=0, help="Max. Number of products for update.")
def update_shop_vx_new_products(limit):
    """Upload new VidaXl products to Shop(s)"""
    from app.controllers import upload_new_products_vidaxl_to_store
    upload_new_products_vidaxl_to_store(limit=limit if limit else None)


@app.cli.command()
@click.option("--limit", default=0, help="Max. Number of products for update.")
def update_shop_vx_delete_products(limit):
    """Upload deleted VidaXl products to Shop(s)"""
    from app.controllers import delete_vidaxl_product_from_store
    delete_vidaxl_product_from_store(limit=limit if limit else None)


@app.cli.command()
@click.option("--limit", default=0, help="Max. Number of products for update.")
def update_shop_vx_changed_products(limit):
    """Upload changed VidaXl products to Shop(s)"""
    from app.controllers import update_products_vidaxl_to_store
    update_products_vidaxl_to_store(limit=limit if limit else None)


@app.cli.command()
@click.option("--limit", default=0, help="Max. Number of products for update.")
def delete_products_from_store_exclude_category(limit):
    """Deletes product from shop for excluded categories"""
    from app.controllers import delete_products_from_store_exclude_category
    delete_products_from_store_exclude_category(limit=limit if limit else None)


@app.cli.command()
@click.option("--limit", default=0, help="Max. Number of products for update.")
def upload_products_to_store_by_category(limit):
    """Update product in shops by categories"""
    from app.controllers import upload_products_to_store_by_category
    upload_products_to_store_by_category(limit=limit if limit else None)


@app.cli.command()
@click.option("--limit", default=0, help="Max. Number of products for update.")
def update_price(limit):
    """Update product in shops by categories"""
    from app.controllers import change_product_price
    change_product_price(limit=limit if limit else None)


@app.cli.command()
def info():
    """Get App Info"""
    import json
    from app.models import Product, Shop, Configuration

    all_products = Product.query
    shops = {s.id: s.name for s in Shop.query.all()}
    data = {
                "Vida products:": all_products.count(),
                "New products:": all_products.filter(
                    Product.is_new == True  # noqa E712
                ).count(),
                "Changed products:": all_products.filter(
                    Product.is_changed == True
                ).count(),
                "Deleted products:": all_products.filter(
                    Product.is_deleted == True
                ).count(),
            }
    csv_check_sum = Configuration.get_common_value("CSV_CHECK_SUM")
    if csv_check_sum:
        data["CSV check sum:"] = csv_check_sum
    vida_updated = Configuration.get_common_value("LAST_VIDAXL_PROD_UPDATED")
    if vida_updated:
        data["Last VidaXl Products updated: %s"] = str(vida_updated)
    if shops:
        data["Shops:"] = shops
    print(
        json.dumps(
            data,
            indent=2,
        )
    )


@app.cli.command()
@click.argument("shop-id")
def shop_info(shop_id):
    """Get App Info"""
    import json
    from app.models import Shop

    shop = Shop.query.get(shop_id)
    if not shop:
        print("Wrong shop id:", shop_id)
        return

    categories = [c.path for c in shop.categories]
    configurations = {}
    for c in shop.configurations:
        if c.path not in configurations:
            configurations[c.path] = {}
        configurations[c.path][c.name] = c.value

    print(
        json.dumps(
            {
                "Shop:": shop.name,
                "Shop products:": len(shop.products),
                "access_token": shop.access_token,
                "private_app_access_token": shop.private_app_access_token,
                "Selected categories": categories,
                "Configurations": configurations,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    app.run()
