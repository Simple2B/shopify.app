#!/user/bin/env python
import click

from app import create_app, db, models, forms

app = create_app()


# flask cli context setup
@app.shell_context_processor
def get_context():
    """Objects exposed here will be automatically available from the shell."""
    return dict(app=app, db=db, m=models, forms=forms)


@app.cli.command()
# @click.confirmation_option(prompt="Drop all database tables?")
def create_db():
    """Create new database."""
    db.create_all()


@app.cli.command()
def scrappy():
    """Test scrap images from VidaXL"""
    # db.drop_all()
    from app.controllers import scrap

    scrap.scrappy_all_products(40)


@app.cli.command()
@click.option("--count", default=0, help="Number of products.")
def update_vidaxl_products(count):
    """Update all products from VidaXl"""
    from app.controllers import download_products

    download_products(count if count > 0 else None)


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
    """Upload all products to Shop(s)"""
    from datetime import datetime
    from app.controllers import (
        upload_new_products_vidaxl_to_store,
        upload_products_to_store_by_category,
        update_products_vidaxl_to_store,
        change_product_price,
        delete_products_from_store_exclude_category,
        delete_vidaxl_product_from_store
        )
    from app.logger import log

    begin = datetime.now()
    # upload_products_to_store_by_category(limit=20)
    # upload_new_products_vidaxl_to_store(limit=20)
    # update_products_vidaxl_to_store(limit=50)
    # delete_products_from_store_exclude_category(limit=2000)
    # delete_vidaxl_product_from_store(limit=30)
    # change_product_price(limit=30)
    log(log.INFO, 'Full loop ended in %d seconds', (datetime.now() - begin).seconds)


@app.cli.command()
def info():
    """Get App Info"""
    import json
    from app.models import Product, Shop

    all_products = Product.query
    shops = {s.id: s.name for s in Shop.query.all()}

    print(
        json.dumps(
            {
                "Vida products:": all_products.count(),
                "New products:": all_products.filter(Product.is_new == True).count(),  # noqa E712
                "Changed products:": all_products.filter(Product.is_changed == True).count(),
                "Deleted products:": all_products.filter(Product.is_deleted == True).count(),
                "Shops:": shops
            },
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

    print(
        json.dumps(
            {
                "Shop:": shop.name,
                "Shop products:": len(shop.products),
                "Selected categories": categories,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    app.run()
