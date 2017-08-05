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