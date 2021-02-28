from app import db
from app.models.utils import ModelMixin


class Shop(db.Model, ModelMixin):
    __tablename__ = 'shops'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, default=False)
    # TODO: more fields
