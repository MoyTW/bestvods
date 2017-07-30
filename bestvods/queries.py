import flask_sqlalchemy as f_alchemy
import sqlalchemy as alchemy
import sqlalchemy.exc as alchemy_exc
import datetime

_insert_game_text = alchemy.text("insert into game values (:name, :release_year, :description)")
_insert_category_text = alchemy.text("insert into category values (:name, :description)")
_insert_platform_text = alchemy.text("insert into platform values (:name, :description)")


def game_exists(db: f_alchemy.SQLAlchemy, name_release_year):
    try:
        release_year = int(name_release_year[-6:].strip('()'))
    except ValueError:
        return False

    result = db.engine.execute('select count(*) from game where name=:name and release_year=:release_year',
                               name=name_release_year[:-6].strip(),
                               release_year=release_year)
    return result.first()[0]


# The following functions have a lot of duplication!
def insert_game(db: f_alchemy.SQLAlchemy, name, release_year: int, description):
    try:
        db.engine.execute(_insert_game_text,
                          name=name.strip(),
                          release_year=release_year,
                          description=description.strip())
        return True
    except alchemy_exc.IntegrityError:
        return False


def category_exists(db: f_alchemy.SQLAlchemy, category):
    return db.engine.execute('select count(*) from category where name=:name', name=category).first()[0]


def insert_category(db: f_alchemy.SQLAlchemy, name, description):
    try:
        db.engine.execute(_insert_category_text,
                          name=name,
                          description=description)
        return True
    except alchemy_exc.IntegrityError:
        return False


def platform_exists(db: f_alchemy.SQLAlchemy, platform):
    return db.engine.execute('select count(*) from platform where name=:name', name=platform).first()[0]


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

_insert_event_text = alchemy.text("insert into event values (:name, :start_date, :end_date, :description)")


def insert_event(db: f_alchemy.SQLAlchemy, name, start_date: datetime.date, end_date: datetime.date, description):
    try:
        db.engine.execute(_insert_event_text,
                          name=name,
                          start_date=start_date,
                          end_date=end_date,
                          description=description)
        return True
    except alchemy_exc.IntegrityError:
        return False


def participant_exists(db: f_alchemy.SQLAlchemy, handle):
    return db.engine.execute('select count(*) from participant where handle=:handle', handle=handle).first()[0]


_insert_participant_text = alchemy.text("insert into participant values (null, :handle, :stream_url)")


def insert_participant(db: f_alchemy.SQLAlchemy, handle, stream_url):
    try:
        db.engine.execute(_insert_participant_text, handle=handle, stream_url=stream_url)
        return True
    except alchemy_exc.IntegrityError:
        return False
