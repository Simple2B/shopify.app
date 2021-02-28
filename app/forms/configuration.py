from flask_wtf import FlaskForm
from wtforms import BooleanField, FloatField, FileField
from wtforms.fields.simple import SubmitField


class ConfigurationForm(FlaskForm):
    leave_vidaxl_prefix = BooleanField("Leave VidaXl prefix: ")
    vidaxl_discount = FloatField("VidaXl discount: ")
    category_rules_file = FileField("Category rule:")
    # TODO: add others configuration parameters
    submit = SubmitField("Save")
