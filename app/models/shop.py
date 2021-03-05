from app import db
from app.models.utils import ModelMixin
from sqlalchemy.orm import relationship


class Shop(db.Model, ModelMixin):
    __tablename__ = "shops"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, default="")
    access_token = db.Column(db.String, default="")
    private_app_access_token = db.Column(db.String, default="")

    configurations = relationship("Configuration")
    products = relationship("ShopProduct")
    categories = relationship("Category")

    def __repr__(self):
        return f"{self.id}) {self.name}"
