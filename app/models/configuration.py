from app import db
from app.models.utils import ModelMixin


class Configuration(db.Model, ModelMixin):

    __tablename__ = 'configurations'

    id = db.Column(db.Integer, primary_key=True)
    prefix_vidaxl = db.Column(db.Boolean, default=False)
    price = db.Column(db.Float, nullable=False, default=0.0)

    def __str__(self):
        return '<Price: %s>' % self.price
