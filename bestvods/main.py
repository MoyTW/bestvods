import os
import flask
import flask_security as security
import bestvods.database
import bestvods.forms as forms
import bestvods.models as models
import bestvods.views as views

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

db = bestvods.database.db


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
    'SECURITY_PASSWORD_SALT': 'not-actually-a-salt',
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + ROOT_DIR + '/../dev/bestvods.db',
    'SECURITY_REGISTERABLE': True,
    'SECURITY_SEND_REGISTER_EMAIL': False
}

app = create_app(default_config)
app.register_blueprint(views.index.blueprint)
app.register_blueprint(views.events.blueprint, url_prefix='/events')
app.register_blueprint(views.games.blueprint, url_prefix='/games')
app.register_blueprint(views.platforms.blueprint, url_prefix='/platforms')
app.register_blueprint(views.vods.blueprint, url_prefix='/vods')
app.register_blueprint(views.participants.blueprint, url_prefix='/participants')
app.register_blueprint(views.recs.blueprint, url_prefix='/recs')
app.register_blueprint(views.tags.blueprint, url_prefix='/tags')

# Setup security
user_datastore = security.SQLAlchemyUserDatastore(db, models.User, models.Role)
security_manager = security.Security(app, user_datastore, register_form=forms.ExtendedRegisterForm)


if __name__ == '__main__':
    app.run()
