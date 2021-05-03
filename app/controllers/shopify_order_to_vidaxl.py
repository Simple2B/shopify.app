def parser_shopify_to_vidaxl(data):
    """[Transformation Shopify order response
    to VidaXL order API format]

    Args:
        data ([json]): [order data]

    Returns:
        [json]: [data for order at VidaXL]
    """
    products = data["line_items"]
    ship_address = data["shipping_address"]
    new_data = {
        "customer_order_reference": data['id'],
        "comments_customer": "Please deliver asap",
        "addressbook": {"country": "FR"},
        "order_products": []
    }
    # shipping address
    addr1 = ship_address["address1"]
    addr2 = ship_address["address2"]
    city = ship_address["city"]
    post_code = ship_address["zip"]
    country = "NL"
    name = ship_address["name"]
    phone = ship_address.get('phone', '')
    address_book = {
        "address": addr1,
        "address2": addr2,
        "city": city,
        "province": "",
        "postal_code": post_code,
        "country": country,
        "name": name,
        "phone": phone,
        "comments": ""
    }
    # product parameters
    for product in products:
        new_prod = {
            "product_code": product["sku"],
            "quantity": int(product["quantity"]),
            "addressbook": address_book
        }
        new_data["order_products"].append(new_prod)
    return new_data
