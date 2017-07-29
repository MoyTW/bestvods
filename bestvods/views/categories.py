import bestvods.utils as utils
import bestvods.queries as queries
import flask
import json
import wtforms
import wtforms.validators as validators

from flask_security import login_required
from bestvods.database import db

blueprint = flask.Blueprint('categories', __name__, template_folder='templates')


@blueprint.route('/', methods=['GET'])
def root():
    term = flask.request.args['term']+'%' if 'term' in flask.request.args else '%'

    if utils.accepts_json(flask.request):
        categories = db.engine.execute('select name from category where name like :term limit 10', term=term).fetchall()
        return flask.Response(json.dumps([g.name for g in categories]), mimetype='application/json')
    else:
        categories = db.engine.execute('select name, description from category where name like :term', term=term)\
            .fetchall()
        strings = [p.name + ": " + p.description for p in categories]
        return flask.render_template('_list.html', list_header='categories', items=strings)


class AddCategoryForm(wtforms.Form):
    name = wtforms.StringField('Name', [validators.DataRequired()], validators.Length(max=256))
    description = wtforms.StringField('Description', [validators.DataRequired(), validators.Length(max=1024)])


@blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddCategoryForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        if queries.insert_category(db, form.name.data, form.description.data):
            flask.flash('Inserted category')
        else:
            flask.flash('Category already exists')
    return flask.render_template('_resource_add.html',
                                 resource_name='Category',
                                 fields=[form.name, form.description])