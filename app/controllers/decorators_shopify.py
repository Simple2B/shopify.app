from functools import wraps
import shopify
from flask import session, redirect, url_for, request, current_app

from app.models import Shop
from app.logger import log


def shopify_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # if "shopify_token" not in session:
        if not shopify.Session.secret:
            shopify.Session.setup(
                api_key=current_app.config["SHOPIFY_API_KEY"],
                secret=current_app.config["SHOPIFY_SECRET"],
            )
            if not shopify.Session.validate_params(request.args):
                log(log.ERROR, "shopify_auth: Wrong arguments in the request")
                return redirect(url_for("shopify_bp.install", **request.args))
            shop = request.args.get("shop")
            log(log.DEBUG, "url: [%s]", shop)
            shop = Shop.query.filter_by(name=shop).first()
            if not shop:
                log(log.ERROR, "shopify_auth: Unknown shop: [%s]", shop)
                return redirect(url_for("shopify_bp.install", **request.args))
            session["shopify_token"] = shop.access_token
            session["shopify_url"] = shop.name
            session["shopify_id"] = shop.id
        else:
            # validation secret
            if shopify.Session.secret != current_app.config["SHOPIFY_SECRET"]:
                log(log.ERROR, "shopify_auth: Wrong arguments in the request")
                return redirect(url_for("shopify_bp.install", **request.args))
            name = request.args.get("shop")
            shop = Shop.query.filter_by(name=name).first()
            if not shop:
                log(log.ERROR, "shopify_auth: Unknown shop: [%s]", name)
                return redirect(url_for("shopify_bp.install", **request.args))
        return f(*args, **kwargs)
    return decorated_function
