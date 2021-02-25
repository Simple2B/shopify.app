import requests
from requests.auth import HTTPBasicAuth
from flask import render_template, Blueprint
from app.logger import log
from app.forms import ShowForm


show_stock_bp = Blueprint('show_stock', __name__)


@show_stock_bp.route('/show_stock', methods=['GET', 'POST'])
def show():
    result = ''
    # return render_template('base.html')
    form = ShowForm()
    if form.validate_on_submit():
        item_id = form.item_id.data
        req = requests.get(
            f'https://b2b.vidaxl.com/api_customer/products?code_eq={item_id}',
            auth=HTTPBasicAuth('jamilya.sars@gmail.com', 'ea5d924f-3531-4550-9e28-9ed5cf76d3f7'))
        resp = req.json()
        log(log.INFO, f'Response: {resp}')
        if float(resp['data'][0]['quantity']) > 1:
            result = f'Item {item_id} in stock'
            return render_template('index.html', form=form, result=result)
    return render_template('index.html', form=form, result=result)
