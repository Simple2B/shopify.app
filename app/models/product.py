from datetime import datetime
from app import db
from app.models.utils import ModelMixin
from sqlalchemy.orm import relationship


class Product(db.Model, ModelMixin):
    """products form VidaXL server"""

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(32), unique=True)
    vidaxl_id = db.Column(db.BigInteger, unique=True)
    is_new = db.Column(db.Boolean, default=True)
    is_changed = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    title = db.Column(db.String(128))
    category_path = db.Column(db.String, default="")
    price = db.Column(db.Float, default=0.0)
    qty = db.Column(db.Integer, default=-1)
    updated = db.Column(db.DateTime, default=datetime.now)
    description = db.Column(db.String)

    shop_products = relationship("ShopProduct")
    images = relationship("Image")

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self):
        return f"<{self.title}({self.sku})>"
