from flask_wtf import FlaskForm
from wtforms import BooleanField, FileField, StringField
from wtforms.fields.core import FloatField, IntegerField
from wtforms.fields.simple import SubmitField


class ConfigurationForm(FlaskForm):
    leave_vidaxl_prefix = BooleanField(
        "Leave VidaXl prefix:",
        default=False,
    )
    category_rules_file = FileField("Category rule:")
    private_app_access_token = StringField("Access Token:", default="")
    mom_selector = BooleanField("Pricing by MoM:", default=False)
    margin_percent = FloatField("Margin percentage:", default=1.0)
    round_to = IntegerField("Defin cents e.g. 50.xx:", default=99)
    # TODO: add others configuration parameters
    submit = SubmitField("Save")
