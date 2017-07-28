import os
import datetime
import json
import flask
import flask_sqlalchemy as alchemy
import flask_security as security
import wtforms
import wtforms.validators as validators
# Decorators don't play nicely with namespaces it seems
from flask_security import login_required
import bestvods.db as db_ops

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


# VoDs
def query_vod(vod_id: int):
    select_game = 'select id, game_name, game_release_year, platform_name, category_name from vod where id=:id'
    select_runners = 'select participant.handle from participant ' \
                     'join vods_runners on participant.id=vods_runners.participant_id ' \
                     'where vod_id=:id'
    select_commentators = 'select participant.handle from participant ' \
                          'join vods_commentators on participant.id=vods_commentators.participant_id ' \
                          'where vod_id=:id'
    vod = db.engine.execute(select_game, id=vod_id).first()
    participants = db.engine.execute(select_runners, id=vod_id).fetchall()
    commentators = db.engine.execute(select_commentators, id=vod_id).fetchall()
    return str(vod) + ' Runner(s): ' + str(participants) + ' Commentators: ' + str(commentators)


@app.route('/vods', methods=['GET'])
def view_vods():
    all_ids = db.engine.execute('select id from vod').fetchall()
    strings = [query_vod(vod_id[0]) for vod_id in all_ids]
    return flask.render_template('_list.html', list_header='VoDs', items=strings)


class AddVoDForm(wtforms.Form):
    game = wtforms.StringField('Game', [validators.DataRequired(), validators.Length(max=256+7)],
                               id='game_autocomplete')
    platform = wtforms.StringField('Platform', [validators.DataRequired(), validators.Length(max=256)])
    category = wtforms.StringField('Category', [validators.DataRequired(), validators.Length(max=256)])
    hours = wtforms.IntegerField('Hours', [validators.DataRequired(), validators.number_range(min=0, max=24*7)])
    minutes = wtforms.IntegerField('Minutes', [validators.DataRequired(), validators.number_range(min=0, max=60)])
    seconds = wtforms.IntegerField('Seconds', [validators.DataRequired(), validators.number_range(min=0, max=60)])


@app.route('/games/_autocomplete', methods=['GET'])
def game_autocomplete():
    print(str(flask.request.args['q']))
    games = db.engine.execute('select name, release_year from game').fetchall()
    strings = [g.name + " (" + str(g.release_year) + ")" for g in games]
    return flask.Response(json.dumps(strings), mimetype='application/json')


@app.route('/vods/add', methods=['GET', 'POST'])
def add_vod():
    form = AddVoDForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        flask.flash(str(form))
    return flask.render_template('vod_add.html', form=form)


# Games
@app.route('/games', methods=['GET'])
def view_games():
    games = db.engine.execute('select name, release_year, description from game').fetchall()
    strings = [g.name + " (" + str(g.release_year) + ") - " + g.description for g in games]
    return flask.render_template('_list.html', list_header='Games', items=strings)


class AddGameForm(wtforms.Form):
    name = wtforms.StringField('Name', [validators.DataRequired(), validators.Length(max=256)])
    this_year = datetime.date.today().year
    release_year = wtforms.IntegerField('Release Year', [validators.DataRequired(),
                                                         validators.number_range(min=1962, max=this_year)])
    description = wtforms.StringField('Description', [validators.DataRequired(), validators.Length(max=1024)])


@app.route('/games/add', methods=['GET', 'POST'])
@login_required
def add_game():
    form = AddGameForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        if db_ops.insert_game(db, form.name.data, form.release_year.data, form.description.data):
            flask.flash('Inserted game')
        else:
            flask.flash('Game already exists')
    return flask.render_template('_resource_add.html',
                                 resource_name='Game',
                                 fields=[form.name, form.release_year, form.description])


# Platforms
@app.route('/platforms', methods=['GET'])
def view_platforms():
    platforms = db.engine.execute('select name, description from platform').fetchall()
    strings = [p.name + ": " + p.description for p in platforms]
    return flask.render_template('_list.html', list_header='Platforms', items=strings)


class AddPlatformForm(wtforms.Form):
    name = wtforms.StringField('Name', [validators.DataRequired(), validators.Length(max=256)])
    description = wtforms.StringField('Description', [validators.DataRequired(), validators.Length(max=1024)])


@app.route('/platforms/add', methods=['GET', 'POST'])
@login_required
def add_platform():
    form = AddPlatformForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        if db_ops.insert_platform(db, form.name.data, form.description.data):
            flask.flash('Inserted platform')
        else:
            flask.flash('Platform already exists')
    return flask.render_template('_resource_add.html',
                                 resource_name='Platform',
                                 fields=[form.name, form.description])


# Categories
@app.route('/categories', methods=['GET'])
def view_categories():
    categories = db.engine.execute('select name, description from category').fetchall()
    strings = [p.name + ": " + p.description for p in categories]
    return flask.render_template('_list.html', list_header='categories', items=strings)


class AddCategoryForm(wtforms.Form):
    name = wtforms.StringField('Name', [validators.DataRequired()], validators.Length(max=256))
    description = wtforms.StringField('Description', [validators.DataRequired(), validators.Length(max=1024)])


@app.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    form = AddCategoryForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        if db_ops.insert_category(db, form.name.data, form.description.data):
            flask.flash('Inserted category')
        else:
            flask.flash('Category already exists')
    return flask.render_template('_resource_add.html',
                                 resource_name='Category',
                                 fields=[form.name, form.description])

if __name__ == '__main__':
    app.run()
