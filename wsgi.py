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
def update_shop_products():
    """Upload all products to Shop(s)"""
    from app.controllers import upload_product
    from app.models import Shop
    from app.logger import log

    for shop in Shop.query.all():
        try:
            upload_product(shop.id)
        except Exception as e:
            log(log.ERROR, "%s", e)
            log(log.CRITICAL, "Error update products in: %s", shop)


@app.cli.command()
def info():
    """Get App Info"""
    import json
    from app.models import Product, Shop

    all_products = Product.query
    shops = {s.id: s.name for s in Shop.query.all()}

    print(
        json.dumps(
            {"Vida products:": all_products.count(), "Shops:": shops},
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
