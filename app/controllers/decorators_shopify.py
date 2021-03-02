import shopify
from functools import wraps
from flask import session, redirect, url_for, request, current_app

from app.models import Shop
from app.logger import log


def shopify_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "shopify_token" not in session:
            shop_url = request.args.get("shop")
            log(log.DEBUG, "url: [%s]", shop_url)
            shopify.Session.setup(
                api_key=current_app.config["SHOPIFY_API_KEY"],
                secret=current_app.config["SHOPIFY_SECRET"],
            )
            if not shopify.Session.validate_params(request.args):
                log(log.ERROR, "We have a problem")
                return redirect(url_for("shopify_bp.install", **request.args))
            shop = Shop.query.filter_by(name=shop_url).first()
            if not shop:
                log(log.ERROR, "Unknown shop: [%s]", shop_url)
                return redirect(url_for("shopify_bp.install", **request.args))
            session["shopify_token"] = shop.access_token
            session["shopify_url"] = shop_url
            session["shopify_id"] = shop.id
        else:
            name = session["shopify_url"]
            shop = Shop.query.filter_by(name=name).first()
            if not shop:
                log(log.ERROR, "Unknown shop: [%s]", name)
                session.pop("shopify_token")
                session.pop("shopify_url")
                session.pop("shopify_id")
                return redirect(url_for("shopify_bp.install", **request.args))
        return f(*args, **kwargs)

    return decorated_function
