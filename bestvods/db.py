import flask_sqlalchemy as f_alchemy
import sqlalchemy as alchemy
import sqlalchemy.exc as alchemy_exc

_insert_game_text = alchemy.text("insert into game values (:name, :release_year, :description)")
_insert_category_text = alchemy.text("insert into category values (:name, :description)")
_insert_platform_text = alchemy.text("insert into platform values (:name, :description)")


# The following functions have a lot of duplication!
def insert_game(db: f_alchemy.SQLAlchemy, name, release_year: int, description):
    try:
        db.engine.execute(_insert_game_text,
                          name=name,
                          release_year=release_year,
                          description=description)
        return True
    except alchemy_exc.IntegrityError:
        return False


def insert_category(db: f_alchemy.SQLAlchemy, name, description):
    try:
        db.engine.execute(_insert_category_text,
                          name=name,
                          description=description)
        return True
    except alchemy_exc.IntegrityError:
        return False


def insert_platform(db: f_alchemy.SQLAlchemy, name, description):
    try:
        db.engine.execute(_insert_platform_text,
                          name=name,
                          description=description)
        return True
    except alchemy_exc.IntegrityError:
        return False


# This one will wait a bit
def insert_tag(db: f_alchemy.SQLAlchemy, name, description):
    pass
