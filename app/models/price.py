from app import db
from app.models.utils import ModelMixin


class Price(db.Model, ModelMixin):

    __tablename__ = 'prices'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)

    def __str__(self):
        return '<Price: %s>' % self.price
