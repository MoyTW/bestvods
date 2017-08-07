import flask_security as security

from bestvods.database import db
from typing import List


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
    username = db.Column(db.String(64), unique=True)
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

    @staticmethod
    def query_by_name_release_year(name_release_year):
        name, release_year = Game.parse_name_release_year(name_release_year)
        return Game.query.filter_by(name=name, release_year=release_year).first()

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
    name = db.Column(db.String(255), nullable=False, unique=True)
    date_start = db.Column(db.Date, nullable=False)
    date_end = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(2048), nullable=False)

    def __init__(self, name, date_start, date_end, description):
        self.name = name
        self.date_start = date_start
        self.date_end = date_end
        self.description = description


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


class VodLink(Base):
    url = db.Column(db.String(2048), unique=True, nullable=False)
    vod_id = db.Column(db.Integer, db.ForeignKey('vod.id'), nullable=False)

    def __init__(self, url, vod_id):
        self.url = url
        self.vod_id = vod_id


class Vod(Base):
    run_time_seconds = db.Column(db.Integer, nullable=False)
    date_completed = db.Column(db.Date, nullable=False)

    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    game = db.relationship('Game')
    platform = db.relationship('Platform')
    category = db.relationship('Category')

    # links should be a 1...n relationship with n >= 1; however, the logical relational database model used by SQL
    # doesn't actually support these semantics. This means links is in an awkward place, and that constraint must be
    # enforced in the application.
    #
    # These links should logically be managed inside of Vod, as opposed to game/platform/events/runners which are
    # resources not depending on Vod.
    links = db.relationship('VodLink')

    event = db.relationship('Event', secondary=vods_event, backref=db.backref('vods', lazy='dynamic'))
    runners = db.relationship('Participant', secondary=vods_runners, backref=db.backref('run_vods', lazy='dynamic'))
    commentators = db.relationship('Participant', secondary=vods_commentators,
                                   backref=db.backref('commentated_vods', lazy='dynamic'))

    def __init__(self, game, platform, category, run_time_seconds, date_completed):
        self.run_time_seconds = run_time_seconds
        self.date_completed = date_completed

        # The relationships can infer the ID fields when you set the object
        self.game = game
        self.platform = platform
        self.category = category

    @staticmethod
    def create_with_related(name_release_year, platform_name, category_name, run_time_seconds, date_completed,
                            event_name, link_urls: List[str], runner_handles: List[str],
                            commentator_handles: List[str]):
        game = Game.query_by_name_release_year(name_release_year)
        vod = Vod(game,
                  Platform.query.filter_by(name=platform_name).first(),
                  Category.query.filter_by(game_id=game.id, name=category_name).first(),
                  run_time_seconds,
                  date_completed)
        if event_name is not None:
            vod.event = Event.query.filter_by(name=event_name).first()
        for link_url in link_urls:
            vod.links.append(VodLink(link_url, vod.id))
        vod.runners = Participant.query.filter(Participant.handle.in_(runner_handles)).all()
        vod.commentators = Participant.query.filter(Participant.handle.in_(commentator_handles)).all()
        return vod


class Tag(Base):
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.String(2048), nullable=False)

    def __init__(self, name, description):
        self.name = name
        self.description = description


user_recs_tags = db.Table('user_recs_tags',
                          db.Column('user_rec_id', db.Integer(), db.ForeignKey('user_rec.id')),
                          db.Column('tag_id', db.Integer(), db.ForeignKey('tag.id')),
                          db.PrimaryKeyConstraint('user_rec_id', 'tag_id'))


class UserRec(Base):
    description = db.Column(db.String(2048), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vod_id = db.Column(db.Integer, db.ForeignKey('vod.id'), nullable=False)

    user = db.relationship('User')
    vod = db.relationship('Vod')

    tags = db.relationship('Tag', secondary=user_recs_tags, backref=db.backref('recs', lazy='dynamic'))

    __table_args__ = (db.UniqueConstraint('user_id', 'vod_id'),)

    def __init__(self, user, vod_id, description, tags):
        self.description = description
        self.vod_id = vod_id

        self.user = user
        self.tags = tags

    @staticmethod
    def create_with_related(username, vod_id: int, description, tag_names: List[str]):
        user_rec = UserRec(User.query.filter_by(username=username).first(),
                           vod_id,
                           description,
                           Tag.query.filter(Tag.name.in_(tag_names)).all())
        return user_rec
