from app.models import Category
from app.logger import log


def update_categories(shop_id: int, file):
    Category.query.filter(Category.shop_id == shop_id).delete()
    for line in file.readlines():
        path = line.decode().strip(" \t\n\r")
        if path:
            log(log.INFO, "Add category: [%s]", path)
            Category(
                shop_id=shop_id,
                path=path,
            ).save()
