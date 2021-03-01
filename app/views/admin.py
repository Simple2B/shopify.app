from flask import (
    redirect,
    url_for,
    render_template,
    session,
    Blueprint,
    flash,
    request
)
from app.forms import CheckProductForm, ConfigurationForm
from app.models import Configuration
from app.vida_xl import VidaXl
from app.logger import log

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")


@admin_blueprint.route("/show_stock", methods=["POST"])
def show_stock():
    form = CheckProductForm()
    if form.validate_on_submit():
        log(log.DEBUG, "Form [/show_stock] validate on submit.")
        item_id = form.item_id.data
        log(log.DEBUG, "Get item_id: [%s]", item_id)
        session["productStock"] = f"Item {item_id} in stock"
        if not float(VidaXl().get_product()["data"][0]["quantity"]) >= 1:
            session["productStock"] = f"Item {item_id} is not in stock"
        return redirect(url_for(url_for("admin.admin")))
    return redirect(url_for("admin.admin"))


@admin_blueprint.route("/<int:shop_id>", methods=["GET", "POST"])
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