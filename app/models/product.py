from datetime import datetime
from app import db
from app.models.utils import ModelMixin


class Product(db.Model, ModelMixin):
    """products form VidaXL server"""

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String, unique=True)
    is_new = db.Column(db.Boolean, default=True)
    is_changed = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    title = db.Column(db.String)
    category_path = db.Column(db.String, default="")
    price = db.Column(db.Float, default=0.0)
    qty = db.Column(db.Integer, default=-1)
    updated = db.Column(db.DateTime, default=datetime.now)

    def __str__(self):
        return f"<title: {self.title}>"
