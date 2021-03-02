from flask import (
    redirect,
    url_for,
    render_template,
    Blueprint,
    flash,
    request
)
from app.forms import ConfigurationForm
from app.models import Configuration
from app.logger import log
from app.controllers import shopify_auth_required

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")


@admin_blueprint.route("/<int:shop_id>", methods=["GET", "POST"])
@shopify_auth_required
def admin(shop_id):
    form = ConfigurationForm(request.form)
    form.shop_id = shop_id
    if form.validate_on_submit():
        log(log.DEBUG, "Form validate with succeed!")
        Configuration.set_value(shop_id, "LEAVE_VIDAXL_PREFIX", form.leave_vidaxl_prefix.data)
        return redirect(url_for("admin.admin", shop_id=shop_id))
    if form.is_submitted():
        log(log.ERROR, "%s", form.errors)
        for error in form.errors:
            for msg in form.errors[error]:
                flash(msg, "warning")

    form.leave_vidaxl_prefix.data = Configuration.get_value(shop_id, "LEAVE_VIDAXL_PREFIX")
    return render_template("index.html", form=form)
