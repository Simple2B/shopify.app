from app import db
from app.models.utils import ModelMixin
from sqlalchemy.orm import relationship


class Category(db.Model, ModelMixin):

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey("shops.id"), nullable=False)
    path = db.Column(db.String, default="?", convert_unicode=True, _expect_unicode=True)

    shop = relationship("Shop")

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<{self.path} (for shop:{self.shop.name})>"
