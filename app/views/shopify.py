# flake8: noqa E501
import uuid
import json
import logging

from flask import (
    Blueprint,
    redirect,
    url_for,
    request,
    render_template,
    current_app,
    session,
)

from app.views import helpers
from app.views.shopify_client import ShopifyStoreClient
from app.vida_xl import VidaXl
from app.models import Shop

# import shopify

shopify_app_blueprint = Blueprint("shopify", __name__)

# ACCESS_TOKEN = None
NONCE = None
ACCESS_MODE = (
    []
)  # Defaults to offline access mode if left blank or omitted. https://shopify.dev/concepts/about-apis/authentication#api-access-modes
SCOPES = ["write_script_tags"]  # https://shopify.dev/docs/admin-api/access-scopes


@shopify_app_blueprint.route("/app_launched", methods=["GET"])
@helpers.verify_web_call
def app_launched():
    global NONCE

    shop_name = request.args.get("shop")
    shop = Shop.query.filter(Shop.name == shop_name).first()
    if shop:

        return redirect(url_for("admin.admin", shop_id=shop.id))
        # update_product() # You can also input [version_api] arg, default arg is "2021-01" # noqa 501
        # return "Memo app (admin)"

    # The NONCE is a single-use random value we send to Shopify so we know the next call from Shopify is valid (see #app_installed) # noqa 501
    #   https://en.wikipedia.org/wiki/Cryptographic_nonce
    NONCE = uuid.uuid4().hex
    redirect_url = helpers.generate_install_redirect_url(
        shop=shop_name, scopes=SCOPES, nonce=NONCE, access_mode=ACCESS_MODE
    )
    return redirect(redirect_url, code=302)


@shopify_app_blueprint.route("/app_installed", methods=["GET"])
@helpers.verify_web_call
def app_installed():
    state = request.args.get("state")
    global NONCE

    # Shopify passes our NONCE, created in #app_launched, as the `state` parameter, we need to ensure it matches!
    if state != NONCE:
        return "Invalid `state` received", 400
    NONCE = None

    # Ok, NONCE matches, we can get rid of it now (a nonce, by definition, should only be used once)
    # Using the `code` received from Shopify we can now generate an access token that is specific to the specified `shop` with the
    #   ACCESS_MODE and SCOPES we asked for in #app_installed
    shop_name = request.args.get("shop")
    code = request.args.get("code")
    access_token = ShopifyStoreClient.authenticate(shop=shop_name, code=code)
    if access_token:
        Shop(
            name=shop_name,
            access_token=access_token,
        ).save()

    # We have an access token! Now let's register a webhook so Shopify will notify us if/when the app gets uninstalled
    # NOTE This webhook will call the #app_uninstalled function defined below
    shopify_client = ShopifyStoreClient(shop=shop_name, access_token=access_token)
    shopify_client.create_webook(
        address=current_app.config["WEBHOOK_APP_UNINSTALL_URL"], topic="app/uninstalled"
    )

    redirect_url = helpers.generate_post_install_redirect_url(shop=shop_name)
    return redirect(redirect_url, code=302)


# @shopify_app_blueprint.route('/rendering_template', methods=['GET'])
# @helpers.redirect_render_url
# def rendering_template():
#     request
#     shop = request.args.get('shop')
#     return render_template('index.html', shop=shop)


@shopify_app_blueprint.route("/app_uninstalled", methods=["POST"])
@helpers.verify_webhook_call
def app_uninstalled():
    # https://shopify.dev/docs/admin-api/rest/reference/events/webhook?api[version]=2020-04
    # Someone uninstalled your app, clean up anything you need to
    # NOTE the shop ACCESS_TOKEN is now void!
    global ACCESS_TOKEN
    ACCESS_TOKEN = None

    webhook_topic = request.headers.get("X-Shopify-Topic")
    webhook_payload = request.get_json()
    logging.error(
        f"webhook call received {webhook_topic}:\n{json.dumps(webhook_payload, indent=4)}"
    )

    return "OK"


@shopify_app_blueprint.route("/data_removal_request", methods=["POST"])
@helpers.verify_webhook_call
def data_removal_request():
    # https://shopify.dev/tutorials/add-gdpr-webhooks-to-your-app
    # Clear all personal information you may have stored about the specified shop
    return "OK"
