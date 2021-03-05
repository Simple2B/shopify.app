import shopify
from flask import (
    Blueprint,
    render_template,
    current_app,
    request,
    redirect,
    session,
    url_for,
)

from app.models import Shop
from app.logger import log


shopify_bp = Blueprint("shopify_bp", __name__, url_prefix="/shopify")


@shopify_bp.route("/install")
def install():
    """Redirect user to permission authorization page."""

    shop_url = request.args.get("shop")
    log(log.DEBUG, "url: [%s]", shop_url)
    shopify.Session.setup(
        api_key=current_app.config["SHOPIFY_API_KEY"],
        secret=current_app.config["SHOPIFY_SECRET"],
    )

    session = shopify.Session(shop_url, version=current_app.config["VERSION_API"])
    log(log.DEBUG, "session: [%s]", session)
    scope = ["write_products", "read_products", "read_script_tags", "write_script_tags"]
    # permission_url = session.create_permission_url(
    #     scope, url_for("shopify_bp.finalize", _external=True)
    # )
    permission_url = session.create_permission_url(
        scope, f"https://{current_app.config['HOST_NAME']}/shopify/finalize"
    )
    log(log.DEBUG, "permission_url: [%s]", permission_url)
    return render_template("shopify_bp/install.html", permission_url=permission_url)


@shopify_bp.route("/finalize")
def finalize():
    """Generate shop token and store the shop information."""

    shop_url = request.args.get("shop")
    log(log.DEBUG, "url: [%s]", shop_url)
    shopify.Session.setup(
        api_key=current_app.config["SHOPIFY_API_KEY"],
        secret=current_app.config["SHOPIFY_SECRET"],
    )
    shopify_session = shopify.Session(
        shop_url, version=current_app.config["VERSION_API"]
    )
    log(log.DEBUG, "session: [%s]", shopify_session)
    token = shopify_session.request_token(request.args)
    log(log.DEBUG, "token: [%s]", token)
    shop = Shop.query.filter(Shop.name == shop_url).first()
    if not shop:
        shop = Shop(name=shop_url, access_token=token)
        shop.save()

    session["shopify_url"] = shop_url
    session["shopify_token"] = token
    session["shopify_id"] = shop.id

    return redirect(url_for("admin.admin", shop_id=shop.id, shop=shop_url))
