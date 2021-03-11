from app.models import Category, Shop, Configuration
from app.logger import log


def update_categories(shop_id: int, file):
    lines = file.readlines()
    if lines:
        Category.query.filter(Category.shop_id == shop_id).delete()
        for line in lines:
            path = line.decode().strip(" \t\n\r")
            if path:
                log(log.INFO, "Add category: [%s]", path)
                Category(
                    shop_id=shop_id,
                    path=path,
                ).save()


PARAMETERS = [
    "LEAVE_VIDAXL_PREFIX",
    "MOM_SELECTOR",
    "MARGIN_PERCENT",
    "ROUND_TO"
]


def get_categories_configuration_tree(shop_id):
    """generates JSON tree for configuration parameters per product category

    Args:
        shop_id (int): shop id
    """
    def add_parameters(node, path):
        for name in PARAMETERS:
            node[name] = Configuration.get_value(shop_id, name, path)

    data = {
        "category": "/",
        "children": []
    }
    add_parameters(data, "/")

    shop = Shop.query.get(shop_id)
    for category in shop.categories:
        children = data["children"]
        path = ""
        for sub_name in category.path.split("/"):
            path += sub_name
            if sub_name not in [c["category"] for c in children]:
                node = {
                    "category": sub_name,
                    "children": []
                }
                add_parameters(node, path)
                children += [node]
                children = node["children"]
            else:
                node = [c for c in children if c["category"] == sub_name][0]
                children = node["children"]
            path += "/"
    return data


def apply_categories_configuration_tree(shop_id: int, data: dict):
    """apply JSON tree configuration for all parameters per category

    Args:
        shop_id (int): shop id
        data (dict): JSON string data
    """
    def apply_parameters(node, path):
        for name in PARAMETERS:
            if name not in node:
                log(log.ERROR, "apply_parameters no value of [%s]", name)
                continue
            Configuration.set_value(shop_id, name, node[name], path)

    apply_parameters(data, "/")

    def apply_node(children, path):
        for node in children:
            path += node["category"]
            apply_parameters(node, path)
            children = node["children"]
            if children:
                path += "/"
                apply_node(children, path)

    children = data["children"]
    path = ""
    apply_node(children, path)
