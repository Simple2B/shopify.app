from app import db
from app.models.utils import ModelMixin
from sqlalchemy.orm import relationship


class ShopProduct(db.Model, ModelMixin):
    """links to shop products"""

    __tablename__ = "shop_products"

    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey("shops.id"), nullable=False)
    shop_product_id = db.Column(db.BigInteger, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    price = db.Column(db.Float, nullable=False)

    shop = relationship("Shop")
    product = relationship("Product")

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self):
        return f"<{self.product_id}: ({self.shop_product_id})>"
