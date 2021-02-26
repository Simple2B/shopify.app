def price_generator(purchase_price, mom=None, margin=None, round_to=None):
    """Generate new price

    Args:
        purchase_price (str or int): Purchase price
        mom (str or int, optional): Price at Mall of Master. Defaults to None.
        margin (str or int, optional): Margin procent. Defaults to None.
        round_to (str or int, optional): Round to (e.g. xx.99) Defaults to None.

    Returns:
        [dict]: Data for update product price
    """
    new_price = None
    if mom:
        if float(purchase_price) * (float(margin)/100+1) > float(mom):
            new_price = float(purchase_price) * (float(margin)/100+1)
        else:
            new_price = float(mom) - 0.01
    elif margin:
        new_price = float(purchase_price) * (float(margin)/100+1)
    elif round_to:
        new_price = round(float(purchase_price)) - (1 - float(round_to))
    return {'product': {'price': str(new_price)}}
