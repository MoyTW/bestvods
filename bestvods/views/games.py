import bestvods.queries as queries
import bestvods.utils as utils
import datetime
import flask
import json
import wtforms
import wtforms.validators as validators

from flask_security import login_required
from bestvods.database import db


blueprint = flask.Blueprint('games', __name__, template_folder='templates')


# TODO: Magic numbers in autocomplete, page size
@blueprint.route('/', methods=['GET'])
def root():
    term = flask.request.args['term']+'%' if 'term' in flask.request.args else '%'

    if utils.accepts_json(flask.request):
        games = db.engine.execute("select name, release_year from game where name like :term limit 10",
                                  term=term).fetchall()
        strings = [g.name + " (" + str(g.release_year) + ")" for g in games]
        return flask.Response(json.dumps(strings), mimetype='application/json')
    else:
        # Add pagination
        games = db.engine.execute('select name, release_year, description from game where name like :term limit 50',
                                  term=term).fetchall()
        strings = [g.name + " (" + str(g.release_year) + ") - " + g.description for g in games]
        return flask.render_template('_list.html', list_header='Games', items=strings)


class AddGameForm(wtforms.Form):
    name = wtforms.StringField('Name', [validators.DataRequired(), validators.Length(max=256)])
    this_year = datetime.date.today().year
    release_year = wtforms.IntegerField('Release Year', [validators.DataRequired(),
                                                         validators.number_range(min=1962, max=this_year)])
    description = wtforms.StringField('Description', [validators.DataRequired(), validators.Length(max=1024)])


@blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddGameForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        if queries.insert_game(db, form.name.data, form.release_year.data, form.description.data):
            flask.flash('Inserted game')
        else:
            flask.flash('Game already exists')
    return flask.render_template('_resource_add.html',
                                 resource_name='Game',
                                 fields=[form.name, form.release_year, form.description])


@blueprint.route('/<string:name_release_year>/')
def name_release_year_handler(name_release_year):
    game = queries.select_game(db, name_release_year)
    if game is not None:
        return flask.render_template('_list.html', list_header=name_release_year, items=game)
    else:
        flask.abort(404)


# Blueprints aren't nestable! That would be my first choice.
@blueprint.route('/<string:name_release_year>/categories/', methods=['GET'])
def categories_root(name_release_year):
    game = queries.select_game(db, name_release_year)
    if game is None:
        flask.abort(404)

    term = flask.request.args['term']+'%' if 'term' in flask.request.args else '%'

    if utils.accepts_json(flask.request):
        categories = db.engine.execute('select name from category '
                                       'where game_id=:game_id and name like :term limit 10',
                                       game_id=game['id'], term=term).fetchall()
        return flask.Response(json.dumps([g.name for g in categories]), mimetype='application/json')
    else:
        categories = db.engine.execute('select name, description from category '
                                       'where game_id=:game_id and name like :term limit 50',
                                       game_id=game['id'], term=term).fetchall()
        strings = [p.name + ": " + p.description for p in categories]
        return flask.render_template('_list.html', list_header='categories for '+game['name'], items=strings)


class AddCategoryForm(wtforms.Form):
    name = wtforms.StringField('Name', [validators.DataRequired(), validators.Length(max=256)])
    description = wtforms.StringField('Description', [validators.DataRequired(), validators.Length(max=1024)])


@blueprint.route('/<string:name_release_year>/categories/add', methods=['GET', 'POST'])
@login_required
def categories_add(name_release_year):
    game = queries.select_game(db, name_release_year)
    if game is None:
        flask.abort(404)

    form = AddCategoryForm(flask.request.form)

    if flask.request.method == 'POST' and form.validate():
        if queries.insert_category(db, game['id'], form.name.data, form.description.data):
            flask.flash('Inserted category')
        else:
            flask.flash('Category already exists')
    return flask.render_template('_resource_add.html',
                                 resource_name='Category',
                                 fields=[form.name, form.description])