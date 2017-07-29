import bestvods.queries as queries
import flask
import wtforms
import wtforms.validators as validators

from flask_security import login_required
from bestvods.database import db

blueprint = flask.Blueprint('platforms', __name__, template_folder='templates')


@blueprint.route('/platforms', methods=['GET'])
def view_platforms():
    platforms = db.engine.execute('select name, description from platform').fetchall()
    strings = [p.name + ": " + p.description for p in platforms]
    return flask.render_template('_list.html', list_header='Platforms', items=strings)


class AddPlatformForm(wtforms.Form):
    name = wtforms.StringField('Name', [validators.DataRequired(), validators.Length(max=256)])
    description = wtforms.StringField('Description', [validators.DataRequired(), validators.Length(max=1024)])


@blueprint.route('/platforms/add', methods=['GET', 'POST'])
@login_required
def add_platform():
    form = AddPlatformForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        if queries.insert_platform(db, form.name.data, form.description.data):
            flask.flash('Inserted platform')
        else:
            flask.flash('Platform already exists')
    return flask.render_template('_resource_add.html',
                                 resource_name='Platform',
                                 fields=[form.name, form.description])