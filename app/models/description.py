from app import db
from app.models.utils import ModelMixin
from sqlalchemy.orm import relationship


class Description(db.Model, ModelMixin):
    __tablename__ = "descriptions"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    text = db.Column(db.String)

    product = relationship("Product")

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self):
        return f"<[{self.id}]: {self.text}(product_id: {self.product_id})>"
