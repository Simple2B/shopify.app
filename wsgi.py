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
@click.confirmation_option(prompt="Drop all database tables?")
def reset_db():
    """Resebase the current database."""
    db.drop_all()
    db.create_all()


@app.cli.command()
def scrappy():
    """Test scrap images from VidaXL"""
    # db.drop_all()
    from app.controllers import scrap
    scrap.scrappy_all_products(40)


@app.cli.command()
def update_vidaxl_products():
    """Update all products from VidaXl
    """
    from app.controllers import download_products
    download_products()


@app.cli.command()
def update_shop_products():
    """Update all products from VidaXl
    """
    from app.controllers import upload_product
    from app.models import Shop
    from app.logger import log
    for shop in Shop.query.all():
        try:
            upload_product(shop.id)
        except Exception as e:
            log(log.ERROR, "%s", e)
            log(log.CRITICAL, "Error update products in: %s", shop)


if __name__ == '__main__':
    app.run()
