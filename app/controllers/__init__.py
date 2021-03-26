# flake8: noqa F401
from .scrap import scrap_img, scrap_description
from .decorators_shopify import shopify_auth_required
from .products import (
    download_products,
    upload_new_products_vidaxl_to_store,
    upload_products_to_store_by_category,
    update_products_vidaxl_to_store,
    delete_vidaxl_product_from_store,
    delete_products_from_store_exclude_category,
    change_product_price,
    change_vida_prefix_title
)
from .categories import (
    update_categories,
    get_categories_configuration_tree,
    apply_categories_configuration_tree,
    reset_config_parameters
)
from .shop import update_access_token, set_csv_url, get_csv_url
from .price import get_price
from .shopify_order_to_vidaxl import parser_shopify_to_vidaxl
from .order_parser import order_parser
from .delete_shopify_order import delete_order
