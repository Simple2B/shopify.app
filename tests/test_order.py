import pytest

from app import create_app, db
from .utils import fill_db_by_test_data
from app.controllers import parser_shopify_to_vidaxl

# from config import TestingConfig as conf


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config["TESTING"] = True

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        db.drop_all()
        db.create_all()
        fill_db_by_test_data()
        yield client
        db.session.remove()
        db.drop_all()
        app_ctx.pop()


def test_creating_order(client):
    data = {
        "id": 123456789,
        "email": "tsyboom@gmail.com",
        "closed_at": None,
        "created_at": "2021-03-15T16:53:11+02:00",
        "updated_at": "2021-03-15T16:53:12+02:00",
        "number": 6,
        "note": None,
        "token": "3dc5bd105c8d0aa0cdc095916e72de8f",
        "gateway": "bogus",
        "test": True,
        "total_price": "100.95",
        "subtotal_price": "100.95",
        "total_weight": 0,
        "total_tax": "16.83",
        "taxes_included": True,
        "currency": "UAH",
        "financial_status": "paid",
        "confirmed": True,
        "total_discounts": "0.00",
        "total_line_items_price": "100.95",
        "cart_token": None,
        "buyer_accepts_marketing": False,
        "name": "#1006",
        "referring_site": "https://third-testing-store.myshopify.com/products/vidaxl-12panel-folding-exhibition-display-wall-242x200-cm-black",
        "landing_site": "/wallets/checkouts.json",
        "cancelled_at": None,
        "cancel_reason": None,
        "total_price_usd": "3.64",
        "checkout_token": "15530dad0ae9a7fab41dd252db5f49f2",
        "reference": None,
        "user_id": None,
        "location_id": None,
        "source_identifier": None,
        "source_url": None,
        "processed_at": "2021-03-15T16:53:10+02:00",
        "device_id": None,
        "phone": None,
        "customer_locale": "en",
        "app_id": 580111,
        "browser_ip": "93.75.251.66",
        "client_details": {
            "accept_language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6",
            "browser_height": 969,
            "browser_ip": "93.75.251.66",
            "browser_width": 1903,
            "session_hash": None,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        },
        "landing_site_ref": None,
        "order_number": 1006,
        "discount_applications": [],
        "discount_codes": [],
        "note_attributes": [],
        "payment_details": {
            "credit_card_bin": "1",
            "avs_result_code": None,
            "cvv_result_code": None,
            "credit_card_number": "•••• •••• •••• 1",
            "credit_card_company": "Bogus",
        },
        "payment_gateway_names": ["bogus"],
        "processing_method": "direct",
        "checkout_id": 19729354653905,
        "source_name": "web",
        "fulfillment_status": None,
        "tax_lines": [
            {
                "price": "16.83",
                "rate": 0.2,
                "title": "PDV",
                "price_set": {
                    "shop_money": {"amount": "16.83", "currency_code": "UAH"},
                    "presentment_money": {"amount": "16.83", "currency_code": "UAH"},
                },
            }
        ],
        "tags": "",
        "contact_email": "tsyboom@gmail.com",
        "order_status_url": "https://third-testing-store.myshopify.com/55077830865/orders/3dc5bd105c8d0aa0cdc095916e72de8f/authenticate?key=156c02f0fcc255f09a58b18b551b6831",
        "presentment_currency": "UAH",
        "total_line_items_price_set": {
            "shop_money": {"amount": "100.95", "currency_code": "UAH"},
            "presentment_money": {"amount": "100.95", "currency_code": "UAH"},
        },
        "total_discounts_set": {
            "shop_money": {"amount": "0.00", "currency_code": "UAH"},
            "presentment_money": {"amount": "0.00", "currency_code": "UAH"},
        },
        "total_shipping_price_set": {
            "shop_money": {"amount": "0.00", "currency_code": "UAH"},
            "presentment_money": {"amount": "0.00", "currency_code": "UAH"},
        },
        "subtotal_price_set": {
            "shop_money": {"amount": "100.95", "currency_code": "UAH"},
            "presentment_money": {"amount": "100.95", "currency_code": "UAH"},
        },
        "total_price_set": {
            "shop_money": {"amount": "100.95", "currency_code": "UAH"},
            "presentment_money": {"amount": "100.95", "currency_code": "UAH"},
        },
        "total_tax_set": {
            "shop_money": {"amount": "16.83", "currency_code": "UAH"},
            "presentment_money": {"amount": "16.83", "currency_code": "UAH"},
        },
        "line_items": [
            {
                "id": 9594321830097,
                "variant_id": 39300114448593,
                "title": "vidaXL 12Panel Folding Exhibition Display Wall 242x200 cm Black",
                "quantity": 1,
                "sku": "10107",
                "variant_title": "",
                "vendor": "third_testing_store",
                "fulfillment_service": "manual",
                "product_id": 6549926871249,
                "requires_shipping": True,
                "taxable": True,
                "gift_card": False,
                "name": "vidaXL 12Panel Folding Exhibition Display Wall 242x200 cm Black",
                "variant_inventory_management": "shopify",
                "properties": [],
                "product_exists": True,
                "fulfillable_quantity": 1,
                "grams": 0,
                "price": "100.95",
                "total_discount": "0.00",
                "fulfillment_status": None,
                "price_set": {
                    "shop_money": {"amount": "100.95", "currency_code": "UAH"},
                    "presentment_money": {"amount": "100.95", "currency_code": "UAH"},
                },
                "total_discount_set": {
                    "shop_money": {"amount": "0.00", "currency_code": "UAH"},
                    "presentment_money": {"amount": "0.00", "currency_code": "UAH"},
                },
                "discount_allocations": [],
                "duties": [],
                "admin_graphql_api_id": "gid://shopify/LineItem/9594321830097",
                "tax_lines": [
                    {
                        "title": "PDV",
                        "price": "16.83",
                        "rate": 0.2,
                        "price_set": {
                            "shop_money": {"amount": "16.83", "currency_code": "UAH"},
                            "presentment_money": {
                                "amount": "16.83",
                                "currency_code": "UAH",
                            },
                        },
                    }
                ],
                "origin_location": {
                    "id": 2791489863889,
                    "country_code": "UA",
                    "province_code": "",
                    "name": "third_testing_store",
                    "address1": "test1",
                    "address2": "",
                    "city": "town1",
                    "zip": "00000",
                },
            }
        ],
        "fulfillments": [],
        "refunds": [],
        "total_tip_received": "0.0",
        "original_total_duties_set": None,
        "current_total_duties_set": None,
        "admin_graphql_api_id": "gid://shopify/Order/3641809174737",
        "shipping_lines": [
            {
                "id": 3104799883473,
                "title": "Standard",
                "price": "0.00",
                "code": "Standard",
                "source": "shopify",
                "phone": None,
                "requested_fulfillment_service_id": None,
                "delivery_category": None,
                "carrier_identifier": None,
                "discounted_price": "0.00",
                "price_set": {
                    "shop_money": {"amount": "0.00", "currency_code": "UAH"},
                    "presentment_money": {"amount": "0.00", "currency_code": "UAH"},
                },
                "discounted_price_set": {
                    "shop_money": {"amount": "0.00", "currency_code": "UAH"},
                    "presentment_money": {"amount": "0.00", "currency_code": "UAH"},
                },
                "discount_allocations": [],
                "tax_lines": [],
            }
        ],
        "billing_address": {
            "first_name": "Алик",
            "address1": "Ул.м.слободивны",
            "phone": None,
            "city": "Львов",
            "zip": "79017",
            "province": None,
            "country": "Ukraine",
            "last_name": "Шкуркин",
            "address2": "5/5",
            "company": None,
            "latitude": None,
            "longitude": None,
            "name": "Алик Шкуркин",
            "country_code": "UA",
            "province_code": None,
        },
        "shipping_address": {
            "first_name": "John",
            "address1": "Burgemeester Oudlaan 50",
            "phone": None,
            "city": "Rotterdam",
            "zip": "3062 PP",
            "province": None,
            "country": "NL",
            "last_name": "Шкуркин",
            "address2": "",
            "company": None,
            "latitude": None,
            "longitude": None,
            "name": "John Stuck",
            "country_code": "NL",
            "province_code": None,
        },
        "customer": {
            "id": 5038626996433,
            "email": "tsyboom@gmail.com",
            "accepts_marketing": False,
            "created_at": "2021-03-15T13:06:20+02:00",
            "updated_at": "2021-03-15T17:47:46+02:00",
            "first_name": "Алик",
            "last_name": "Шкуркин",
            "orders_count": 0,
            "state": "disabled",
            "total_spent": "0.00",
            "last_order_id": None,
            "note": None,
            "verified_email": True,
            "multipass_identifier": None,
            "tax_exempt": False,
            "phone": None,
            "tags": "",
            "last_order_name": None,
            "currency": "UAH",
            "accepts_marketing_updated_at": "2021-03-15T13:06:21+02:00",
            "marketing_opt_in_level": None,
            "admin_graphql_api_id": "gid://shopify/Customer/5038626996433",
            "default_address": {
                "id": 6203735474385,
                "customer_id": 5038626996433,
                "first_name": "Алик",
                "last_name": "Шкуркин",
                "company": None,
                "address1": "Ул.м.слободивны",
                "address2": "5/5",
                "city": "Львов",
                "province": None,
                "country": "Ukraine",
                "zip": "79017",
                "phone": None,
                "name": "Алик Шкуркин",
                "province_code": None,
                "country_code": "UA",
                "country_name": "Ukraine",
                "default": True,
            },
        },
    }
    data = parser_shopify_to_vidaxl(data)
    assert data
    if data == {
        "customer_order_reference": 123456789,
        "comments_customer": "Please deliver asap",
        "addressbook": {"country": "FR"},
        "order_products": [
            {
                "product_code": "10107",
                "quantity": 1,
                "addressbook": {
                    "address": "Burgemeester Oudlaan 50",
                    "address2": "",
                    "city": "Rotterdam",
                    "province": "",
                    "postal_code": "3062 PP",
                    "country": "NL",
                    "name": "John Stuck",
                    "phone": None,
                    "comments": "",
                },
            }
        ],
    }:
        assert True
    else:
        assert False
