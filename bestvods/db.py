import flask_sqlalchemy as f_alchemy
import sqlalchemy as alchemy
import sqlalchemy.exc as alchemy_exc

insert_game_text = alchemy.text("insert into game values (:name, :release_year, :description)")


def insert_game(db: f_alchemy.SQLAlchemy, name, release_year: int, description):
    try:
        db.engine.execute(insert_game_text,
                          name=name,
                          release_year=release_year,
                          description=description)
    except alchemy_exc.IntegrityError:
        return False


def insert_category(db: f_alchemy.SQLAlchemy, name, description):
    pass


def insert_tag(db: f_alchemy.SQLAlchemy, name, description):
    pass