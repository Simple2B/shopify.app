from app.controllers import scrap_img
from app.logger import log


def update_product(
    prod_api,
    collect_api,
    prod_id,
    title,
    qty,
    price,
    currency,
    collection,
    item=0,
    limit=1,
):
    if item > limit:
        pass
    else:
        if qty == 0:
            pass
        else:
            images_src = scrap_img(prod_id).get("images", "")
            if title.startswith("vidaXL "):
                title = title.replace("vidaXL ", "")
            collection_id = collect_api.create_collection(
                {"custom_collection": {"title": collection}}
            )
            prod_api.create_product(
                {
                    "product": {
                        "title": title,
                        # "body_html": "<strong>Good snowboard!</strong>",
                        # "vendor": "Burton",
                        "variants": [
                            {
                                # "option1": "First",
                                "inventory_quantity": qty,
                                "price": price,
                                # "sku": "123"
                                "presentment_prices": [
                                    {
                                        "price": {
                                            "currency_code": currency,
                                            "amount": qty,
                                        },
                                        "compare_at_price": None,
                                    }
                                ],
                                "product_id": prod_id,
                            }
                        ],
                        "images": [{"src": img_src} for img_src in images_src],
                    },
                    "status": "active",
                }
            )
            collect_api.put_product(
                {"collect": {"product_id": prod_id, "collection_id": collection_id}}
            )
            log(log.DEBUG, "Product created. Product id: [%d]", prod_id)
