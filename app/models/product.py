from app import db
from app.models.utils import ModelMixin


class Product(db.Model, ModelMixin):

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, unique=True)

    def __str__(self):
        return '<Product VidaXL id: %s>' % self.product_id
