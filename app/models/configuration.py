from app import db
from app.models.utils import ModelMixin
from sqlalchemy.orm import relationship


class Configuration(db.Model, ModelMixin):

    __tablename__ = "configurations"

    id = db.Column(db.Integer, primary_key=True)
    # prefix_vidaxl = db.Column(db.Boolean, default=False)
    # price = db.Column(db.Float, nullable=False, default=0.0)
    shop_id = db.Column(db.Integer, db.ForeignKey("shops.id"), nullable=False)
    name = db.Column(db.String, default="unknown name")
    value = db.Column(db.String, default="")

    shop = relationship("Shop")

    def __str__(self):
        return f"<{self.id}:{self.name}={self.value} (for shop:{self.shop.name})>"
