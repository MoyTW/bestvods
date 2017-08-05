import flask_security as security

from bestvods.database import db


class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    timestamp_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    timestamp_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                                   onupdate=db.func.current_timestamp())

# Users & Roles
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(Base, security.RoleMixin):
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255), nullable=False)


class User(Base, security.UserMixin):
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), nullable=False)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


class Game(Base):
    name = db.Column(db.String(255), nullable=False)
    release_year = db.Column(db.SmallInteger, nullable=False)
    description = db.Column(db.String(2048), nullable=False)
    categories = db.relationship('Category', backref='game', lazy='dynamic')

    __table_args__ = (db.UniqueConstraint('name', 'release_year'),)

    def __init__(self, name, release_year: int, description):
        self.name = name
        self.release_year = release_year
        self.description = description

    @property
    def name_release_year(self):
        return self.name + ' (' + str(self.release_year) + ')'

    @staticmethod
    def parse_name_release_year(name_release_year):
        try:
            return [name_release_year[:-6].strip(), int(name_release_year[-6:].strip('()'))]
        except ValueError:
            return [None, None]

    def __repr__(self):
        return '<Game %r>' % self.name_release_year


class Category(Base):
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(2048), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('name', 'game_id'),)

    def __init__(self, name, description, game_id):
        self.name = name
        self.description = description
        self.game_id = game_id


class Platform(Base):
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(2048), nullable=False)

    def __init__(self, name, description):
        self.name = name
        self.description = description


class Event(Base):
    name = db.Column(db.String(255), nullable=False)
    date_start = db.Column(db.Date, nullable=False)
    date_end = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(2048), nullable=False)


class Participant(Base):
    handle = db.Column(db.String(255), nullable=False, unique=True)
    stream_url = db.Column(db.String(2048), nullable=False)

    def __init__(self, handle, stream_url):
        self.handle = handle
        self.stream_url = stream_url


vods_event = db.Table('vods_event',
                      db.Column('vod_id', db.Integer(), db.ForeignKey('vod.id'), unique=True),
                      db.Column('event_id', db.Integer(), db.ForeignKey('event.id')),
                      db.PrimaryKeyConstraint('vod_id', 'event_id'))

vods_runners = db.Table('vods_runners',
                      db.Column('vod_id', db.Integer(), db.ForeignKey('vod.id')),
                      db.Column('participant_id', db.Integer(), db.ForeignKey('participant.id')),
                      db.PrimaryKeyConstraint('vod_id', 'participant_id'))

vods_commentators = db.Table('vods_commentators',
                             db.Column('vod_id', db.Integer(), db.ForeignKey('vod.id')),
                             db.Column('participant_id', db.Integer(), db.ForeignKey('participant.id')),
                             db.PrimaryKeyConstraint('vod_id', 'participant_id'))


class Vod(Base):
    run_time_seconds = db.Column(db.Integer, nullable=False)
    date_completed = db.Column(db.Date, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    links = db.relationship('VodLinks')
    game = db.relationship('Game')
    event = db.relationship('Event', secondary=vods_event, backref=db.backref('vods', lazy='dynamic'))
    runners = db.relationship('Participant', secondary=vods_runners, backref=db.backref('run_vods', lazy='dynamic'))
    commentators = db.relationship('Participant', secondary=vods_commentators,
                                   backref=db.backref('commentated_vods', lazy='dynamic'))


class VodLinks(Base):
    url = db.Column(db.String(2048), unique=True, nullable=False)
    vod_id = db.Column(db.Integer, db.ForeignKey('vod.id'), nullable=False)
