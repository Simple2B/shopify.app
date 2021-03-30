from datetime import datetime
from app import db
from app.models.utils import ModelMixin
from sqlalchemy.orm import relationship

from flask import current_app
from config import BaseConfig as conf
from app.logger import log


CATEGORY_SPLITTER = conf.CATEGORY_SPLITTER


class Configuration(db.Model, ModelMixin):

    __tablename__ = "configurations"

    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey("shops.id"), nullable=True)
    name = db.Column(db.String, default="unknown name")
    value = db.Column(db.String, default="")
    value_type = db.Column(db.String, default="")
    path = db.Column(db.String, default="/")

    shop = relationship("Shop")

    @staticmethod
    def get_value(shop_id: int, name: str, path="/"):
        if CATEGORY_SPLITTER != '/' and CATEGORY_SPLITTER in path:
            path = path.replace(CATEGORY_SPLITTER, '/')
        conf = (
            Configuration.query.filter(Configuration.shop_id == shop_id)
            .filter(Configuration.name == name)
            .filter(Configuration.path == path)
            .first()
        )
        if not conf:
            conf = (
                Configuration.query.filter(Configuration.shop_id == shop_id)
                .filter(Configuration.name == name)
                .filter(Configuration.path == "/")
                .first()
            )
        if conf:
            return Configuration.get_typed_value(conf.value, conf.value_type)
        return current_app.config.get("ADMIN_" + name, None)

    @staticmethod
    def get_common_value(name: str):
        conf = (
            Configuration.query.filter(Configuration.shop_id == None)  # noqa E711
            .filter(Configuration.name == name)
            .first()
        )
        if conf:
            return Configuration.get_typed_value(conf.value, conf.value_type)
        return current_app.config.get("ADMIN_" + name, None)

    @staticmethod
    def set_value(shop_id: int, name: str, value, path="/"):
        value_type = "str"
        if isinstance(value, bool):
            value_type = "bool"
        elif isinstance(value, float):
            value_type = "float"
        elif isinstance(value, int):
            value_type = "int"

        conf = (
            Configuration.query.filter(Configuration.shop_id == shop_id)
            .filter(Configuration.name == name)
            .filter(Configuration.path == path)
            .first()
        )
        if conf:
            if Configuration.get_typed_value(conf.value, conf.value_type) != value:
                conf.value = str(value)
                conf.value_type = value_type
                conf.save()
        else:
            Configuration(
                shop_id=shop_id,
                name=name,
                value=str(value),
                value_type=value_type,
                path=path,
            ).save()

    @staticmethod
    def set_common_value(name: str, value):
        value_type = "str"
        if isinstance(value, bool):
            value_type = "bool"
        elif isinstance(value, float):
            value_type = "float"
        elif isinstance(value, int):
            value_type = "int"
        elif isinstance(value, datetime):
            value_type = "datetime"
            value = value.isoformat()

        conf = (
            Configuration.query.filter(Configuration.shop_id == None)  # noqa E711
            .filter(Configuration.name == name)
            .first()
        )
        if conf:
            if Configuration.get_typed_value(conf.value, conf.value_type) != value:
                conf.value = str(value)
                conf.value_type = value_type
                conf.save()
        else:
            Configuration(
                name=name,
                value=str(value),
                value_type=value_type,
            ).save()

    @staticmethod
    def get_typed_value(value: str, value_type: str):
        switch = {
            "bool": lambda x: value in ("True", "true", "Y", "y"),
            "float": lambda x: float(x),
            "int": lambda x: int(x),
            "str": lambda x: str(x),
            "datetime": lambda x: datetime.fromisoformat(x),
        }

        if value_type not in switch:
            log(log.ERROR, "No value type found: [%s]", value_type)
            return value

        return switch[value_type](value)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<{self.id}:{self.name}({self.value_type})={self.value} (for shop:{self.shop.name})>"
