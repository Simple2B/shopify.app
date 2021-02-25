from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired


class ShowForm(FlaskForm):
    item_id = StringField('Item_ID', validators=[DataRequired()])
    submit = SubmitField('Check')
