from app.models import Category


def update_categories(shop_id: int, file):
    Category.query.filter(Category.shop_id == shop_id).delete()
    for line in file.readlines():
        Category(
            shop_id=shop_id,
            path=line.decode().strip(" \t\n\r"),
        ).save()
    pass
