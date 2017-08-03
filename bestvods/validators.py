import flask_sqlalchemy as f_alchemy
import wtforms


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
