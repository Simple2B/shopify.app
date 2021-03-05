import io
from datetime import datetime

from flask import (
    render_template,
    Blueprint,
    flash,
    request,
    send_file,
)
from app.forms import ConfigurationForm
from app.models import Configuration, Product, Category
from app.logger import log
from app.controllers import (
    shopify_auth_required,
    update_categories,
    update_access_token,
)

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")


@admin_blueprint.route("/<int:shop_id>", methods=["GET", "POST"])
@shopify_auth_required
def admin(shop_id):
    form = ConfigurationForm(request.form)
    form.shop_id = shop_id
    form.categories = Category.query.filter(Category.shop_id == shop_id).all()
    vidaxl_prefix_conf = Configuration.get_value(shop_id, "LEAVE_VIDAXL_PREFIX")
    if form.validate_on_submit():
        form_vidaxl_prefix = form.leave_vidaxl_prefix.data
        log(log.DEBUG, "Form validate with succeed!")
        if not Configuration.get_value(shop_id, "LEAVE_VIDAXL_PREFIX") == form_vidaxl_prefix:
            Configuration.set_value(
                shop_id, "LEAVE_VIDAXL_PREFIX", form_vidaxl_prefix
            )
        if "category_rules_file" in request.files:
            update_categories(shop_id, request.files["category_rules_file"])
        if form.private_app_access_token.data:
            update_access_token(shop_id, form.private_app_access_token.data)
        flash("Configuration saved", "success")
        log(log.INFO, "Configuration saved")
        return render_template("index.html", form=form, **request.args)
    if form.is_submitted():
        log(log.ERROR, "%s", form.errors)
        for error in form.errors:
            for msg in form.errors[error]:
                flash(msg, "warning")

    form.leave_vidaxl_prefix.data = vidaxl_prefix_conf
    return render_template("index.html", form=form, **request.args)


@admin_blueprint.route("/all_categories", methods=["GET"])
def all_categories():
    mem = io.BytesIO()

    with io.StringIO() as stream:
        data = (
            Product.query.filter(Product.is_deleted == False)  # noqa E712
            .with_entities(Product.category_path)
            .distinct()
            .order_by(Product.category_path)
            .all()
        )
        categories = (r.category_path + "\n" for r in data)
        stream.writelines(categories)
        mem.write(stream.getvalue().encode("utf-8"))
    mem.seek(0)

    return send_file(
        mem,
        as_attachment=True,
        attachment_filename="all_categories.txt",
        mimetype="text/txt",
        cache_timeout=0,
        last_modified=datetime.now(),
    )
