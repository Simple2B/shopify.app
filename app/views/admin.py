from flask import (
    redirect,
    url_for,
    render_template,
    session,
    Blueprint,
    current_app,
    flash,
)
from app.forms import CheckProductForm, ConfigurationForm
from app.models import Shop
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
    form = ConfigurationForm()
    form.shop_id = shop_id
    shop = Shop.query.get(shop_id)
    db_conf = {c.name: c.value for c in shop.configurations}
    if "ADMIN_LEAVE_VIDAXL_PREFIX" in db_conf:
        form.leave_vidaxl_prefix.data = db_conf["ADMIN_LEAVE_VIDAXL_PREFIX"] in (
            "Y",
            "y",
        )
    else:
        form.leave_vidaxl_prefix.data = current_app.config["ADMIN_LEAVE_VIDAXL_PREFIX"]
    form.vidaxl_discount.data = current_app.config["ADMIN_VIDAXL_DISCOUNT"]
    # log(log.DEBUG, 'Next URL : [%s]', next_url)
    if form.validate_on_submit():
        log(log.DEBUG, "Form validate with succeed!")
        # return redirect(url_for("admin.admin", shop_id=shop_id))
        return render_template("index.html", form=form)
    if form.is_submitted():
        log(log.ERROR, "%s", form.errors)
        for error in form.errors:
            for msg in form.errors[error]:
                flash(msg, "warning")
    return render_template("index.html", form=form)
