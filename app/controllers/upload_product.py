from app.controllers import scrap_img
from app.logger import log


def upload_product(
    prod_api,
    collect_api,
    product_id,
    title,
    qty,
    price,
    collection,
):
    if qty == 0:
        pass
    else:
        images_src = scrap_img(product_id).get("images", "")
        if title.startswith("vidaXL "):
            title = title.replace("vidaXL ", "")
        collection_id = collect_api.create_collection(
            {"custom_collection": {"title": collection}}
        )
        res = prod_api.create_product(
            {
                "product": {
                    "title": title,
                    # "body_html": "<strong>Good snowboard!</strong>",
                    # "vendor": "Burton",
                    "variants": [
                        {
                            # "option1": "First",
                            "inventory_item_id": product_id,
                            "price": price,
                            # "sku": "123"
                        }
                    ],
                    "images": [{"src": img_src} for img_src in images_src],
                },
                "status": "active",
            }
        )
        collect_api.put_product(
            {"collect": {"product_id": res['product']['id'], "collection_id": collection_id}}
        )
        prod_api.set_quantity(inventory_item_id=product_id, quantity=qty)
        log(log.DEBUG, "Product created. Product id: [%d]", product_id)
