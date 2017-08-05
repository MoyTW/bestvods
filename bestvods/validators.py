import flask_sqlalchemy as f_alchemy
import wtforms

from bestvods.models import Game, Platform


class _RowExists:
    def __init__(self, allow_empty=False, message=None):
        self.allow_empty = allow_empty
        if not message:
            self.message = u"There's no record of this item!"
        else:
            self.message = message

    def __call__(self, form, field):
        if self.allow_empty and (field.data is None or field.data == ''):
            return


class GameExists(_RowExists):
    def __init__(self, allow_empty=False, message=u"Game not found!"):
        super().__init__(allow_empty=allow_empty, message=message)

    def __call__(self, form, field):
        super().__call__(form, field)

        name, release_year = Game.parse_name_release_year(field.data)
        if Game.query.filter_by(name=name, release_year=release_year).first() is None:
            raise wtforms.ValidationError(self.message)


class PlatformExists(_RowExists):
    def __init__(self, allow_empty=False, message=u"Platform not found!"):
        super().__init__(allow_empty=allow_empty, message=message)

    def __call__(self, form, field):
        super().__call__(form, field)

        if Platform.query.filter_by(name=field.data).first() is None:
            raise wtforms.ValidationError(self.message)


class CategoryExists(_RowExists):
    def __init__(self, game_field_name, allow_empty=False, message=u"Category not found for game!"):
        super().__init__(allow_empty=allow_empty, message=message)

        self.game_field_name = game_field_name

    def __call__(self, form, field):
        super().__call__(form, field)

        game_field = form._fields.get(self.game_field_name)
        name, release_year = Game.parse_name_release_year(game_field.data)
        game = Game.query.filter_by(name=name, release_year=release_year).first()
        if game is None or game.categories.filter_by(name=field.data).first() is None:
            raise wtforms.ValidationError(self.message)


class SatisfiesQuery:
    def __init__(self, db: f_alchemy.SQLAlchemy, query_fn, message=None):
        self.db = db
        self.query_fn = query_fn
        if not message:
            self.message = u'This item does not satisfy some DB-based condition!'
        else:
            self.message = message

    def __call__(self, form, field):
        if not self.query_fn(self.db, field.data):
            raise wtforms.ValidationError(self.message)


class EmptyOrSatisfiesQuery:
    def __init__(self, db: f_alchemy.SQLAlchemy, query_fn, message=None):
        self.db = db
        self.query_fn = query_fn
        if not message:
            self.message = u'This item does not satisfy some DB-based condition!'
        else:
            self.message = message

    def __call__(self, form, field):
        if not field.data == "" and not self.query_fn(self.db, field.data):
            raise wtforms.ValidationError(self.message)
