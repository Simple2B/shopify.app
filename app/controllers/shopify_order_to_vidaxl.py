import json


def parser_shopify_to_vidaxl(data):
    """[Transformation Shopify order response
    to VidaXL order API format]

    Args:
        data ([json]): [order data]

    Returns:
        [json]: [data for order at VidaXL]
    """
    # new_data = {
    #     "customer_order_reference": '123',
    #     'order_products': []
    #     }
    products = data['line_items']
    ship_address = data['shipping_address']
    # # shipping address
    # addr1 = ship_address['address1']
    # addr2 = ship_address['address2']
    # city = ship_address['city']
    # post_code = ship_address['zip']
    # country = ship_address['country']
    # name = ship_address['name']
    # address_book = {
    #     'address': addr1,
    #     'address2': addr2,
    #     'city': city,
    #     'postal_code': post_code,
    #     'country': country,
    #     'name': name
    # }
    # # product parameters
    # for product in products:
    #     new_prod = {
    #         'product_code': int(product['sku']),
    #         'quantity': product['quantity'],
    #         'addressbook': address_book
    #     }
    #     new_data['order_products'].append(new_prod)
    # return new_data
    new_data = {
        "customer_order_reference": 70000001,
        "comments_customer": "Please deliver asap",
        "addressbook": {"country": "FR"},
        "order_products": [
            {
                "product_code": '10107',
                "quantity": 1,
                "addressbook": {
                    "address": "Covent Garden",
                    "address2": "",
                    "city": "London",
                    "province": "",
                    "postal_code": "NR33 7NL",
                    "country": "GB",
                    "name": "Test Company",
                    "phone": "0684541247",
                    "comments": ""
                }
            }
        ]
    }
    # return json.dumps(new_data, indent=2)
    return new_data
