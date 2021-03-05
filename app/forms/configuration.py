from flask_wtf import FlaskForm
from wtforms import BooleanField, FileField, StringField
from wtforms.fields.simple import SubmitField


class ConfigurationForm(FlaskForm):
    leave_vidaxl_prefix = BooleanField(
        "Leave VidaXl prefix:",
        default=False,
    )
    category_rules_file = FileField("Category rule:")
    private_app_access_token = StringField("Access Token:", default="")
    # TODO: add others configuration parameters
    submit = SubmitField("Save")
