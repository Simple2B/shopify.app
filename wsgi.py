#!/user/bin/env python
import click

from app import create_app, db, models, forms
from app.models import Configuration

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
    Configuration().save()


@app.cli.command()
def scrappy():
    """Test scrap images from VidaXL"""
    # db.drop_all()
    from app.controllers import scrap
    from app.logger import log
    log(log.INFO, scrap.scrap_img(35653))


if __name__ == '__main__':
    app.run()
