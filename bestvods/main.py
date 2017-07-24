import os
import flask
import flask_sqlalchemy as alchemy
import flask_security as security
# Decorators don't play nicely with namespaces it seems
from flask_security import login_required

# Create app
app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_PASSWORD_SALT'] = 'not-actually-a-salt'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'bestvods.db')

# Create database connection object
db = alchemy.SQLAlchemy(app)

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

if __name__ == '__main__':
    app.run()
