from flask import Blueprint, request, jsonify
from app.controllers import parser_shopify_to_vidaxl, delete_order
from app.vida_xl import VidaXl

hooks_blueprint = Blueprint("web_hooks", __name__)


@hooks_blueprint.route("/web_hook", methods=["POST"])
def web_hook():
    headers = request.headers.environ
    # 'HTTP_X_SHOPIFY_API_VERSION':'2021-01'
    # 'HTTP_X_SHOPIFY_HMAC_SHA256':'GYf2cJ3TlbLq5B1p79VyTYuLiNRHeIO8ZZ2hAtjmDgQ='
    # 'HTTP_X_SHOPIFY_ORDER_ID':'3638980804814'
    # 'HTTP_X_SHOPIFY_SHOP_DOMAIN':'memo-s2b-store.myshopify.com'
    # 'HTTP_X_SHOPIFY_TEST':'true'
    # 'HTTP_X_SHOPIFY_TOPIC':'orders/create'
    # 'HTTP_X_SHOPIFY_WEBHOOK_ID':'bf21d054-b7b6-4258-ba60-31dd85363970'
    if "HTTP_X_SHOPIFY_ORDER_ID" not in headers:
        return jsonify("OK")
    data = headers["werkzeug.request"].json
    vida = VidaXl()
    order_id = data["id"]
    data = parser_shopify_to_vidaxl(data)
    new_order = vida.create_order(data)
    if not new_order:
        delete_order(order_id)
    return jsonify("OK")