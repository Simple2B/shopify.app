from app.vida_xl import VidaXl


def order_parser():
    """[Parse response from VidaXL]

    Returns:
        [list]: [Data for admin page]
    """
    new_data = []
    vida = VidaXl()
    for order in vida.get_documents():
        new_order = {
            'id': order['order']['customer_order_reference'],
            'status': order['order']['status_order_name'],
            'tracking_url': order['order']['shipping_tracking_url']
        }
        new_data.append(new_order)
    return new_data
