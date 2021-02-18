from app import db
from app.models.utils import ModelMixin


class Token(db.Model, ModelMixin):

    __tablename__ = 'token'

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(60), unique=True)

    def __str__(self):
        return '<Access token: %s>' % self.access_token
