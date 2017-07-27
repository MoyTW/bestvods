import os
import flask
import flask_sqlalchemy as alchemy
import flask_security as security
# Decorators don't play nicely with namespaces it seems
from flask_security import login_required

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

db = alchemy.SQLAlchemy()


def create_app(config):
    new_app = flask.Flask(__name__)
    for k, v in config.items():
        new_app.config[k] = v
    db.init_app(new_app)
    new_app.app_context().push()
    return new_app

default_config = {
    'DEBUG': True,
    'SECRET_KEY': 'super-secret',
    'SECRUITY_PASSWORD_SALT': 'not-actually-a-salt',
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + ROOT_DIR + '/bestvods.db'
}

app = create_app(default_config)

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, security.RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, security.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

# Setup Flask-Security
user_datastore = security.SQLAlchemyUserDatastore(db, User, Role)
security = security.Security(app, user_datastore)


# Create a user to test with
@app.before_first_request
def create_user():
    result = db.engine.execute("select * from user where email = 'matt@nobien.net'").fetchone()
    if result is None:
        print('Adding test user matt@nobien.net')
        user_datastore.create_user(email='matt@nobien.net', password='password')
        db.session.commit()
    pass


# Views
@app.route('/')
@login_required
def home():
    return flask.render_template('index.html')


@app.route('/games', methods=['GET'])
def view_games():
    games = db.engine.execute('select name, release_year, description from game').fetchall()
    return flask.render_template('games.html', games=games)


@app.route('/games/add', methods=['GET', 'POST'])
@login_required
def add_game_get():
    if flask.request.method == 'POST':
        # Add WTForms to help handle this?
        print(flask.request.form)
    return flask.render_template('games_add.html')


if __name__ == '__main__':
    app.run()
