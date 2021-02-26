from flask import render_template, Blueprint
from app.forms import ShowForm

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    form = ShowForm()
    return render_template('index.html', form=form)
