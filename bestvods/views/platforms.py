import bestvods.queries as queries
import bestvods.utils as utils
import flask
import json
import wtforms
import wtforms.validators as validators

from flask_security import login_required
from bestvods.database import db

blueprint = flask.Blueprint('platforms', __name__, template_folder='templates')


@blueprint.route('/', methods=['GET'])
def root():
    term = flask.request.args['term'] + '%' if 'term' in flask.request.args else '%'

    if utils.accepts_json(flask.request):
        platforms = db.engine.execute("select name from platform where name like :term limit 10", term=term).fetchall()
        return flask.Response(json.dumps([g.name for g in platforms]), mimetype='application/json')
    else:
        platforms = db.engine.execute('select name, description from platform where name like :term limit 50')\
            .fetchall()
        strings = [p.name + ": " + p.description for p in platforms]
        return flask.render_template('_list.html', list_header='Platforms', items=strings)


class AddPlatformForm(wtforms.Form):
    name = wtforms.StringField('Name', [validators.DataRequired(), validators.Length(max=256)])
    description = wtforms.StringField('Description', [validators.DataRequired(), validators.Length(max=1024)])


@blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddPlatformForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        if queries.insert_platform(db, form.name.data, form.description.data):
            flask.flash('Inserted platform')
        else:
            flask.flash('Platform already exists')
    return flask.render_template('_resource_add.html',
                                 resource_name='Platform',
                                 fields=[form.name, form.description])