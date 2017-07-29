import bestvods.queries as queries
import flask_sqlalchemy as f_alchemy
import wtforms


class DBValidator:
    def __init__(self, db: f_alchemy.SQLAlchemy, message=None):
        self.db = db
        if not message:
            self.message = u'This item does not exist!'
        else:
            self.message = message


class GameExists(DBValidator):
    def __init__(self, db: f_alchemy.SQLAlchemy, message=u"I don't know about this game!"):
        super().__init__(db, message)

    def __call__(self, form, field):
        if not queries.game_exists(self.db, field.data):
            raise wtforms.ValidationError(self.message)


class PlatformExists(DBValidator):
    def __init__(self, db: f_alchemy.SQLAlchemy, message=u"I don't know about this platform!"):
        super().__init__(db, message)

    def __call__(self, form, field):
        if not queries.platform_exists(self.db, field.data):
            raise wtforms.ValidationError(self.message)


class CategoryExists(DBValidator):
    def __init__(self, db: f_alchemy.SQLAlchemy, message=u"I don't know about this category!"):
        super().__init__(db, message)

    def __call__(self, form, field):
        if not queries.category_exists(self.db, field.data):
            raise wtforms.ValidationError(self.message)
