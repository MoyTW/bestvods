import bestvods.utils as utils
import flask
import json
import sqlalchemy.exc
import wtforms
import wtforms.validators as validators

from flask_security import login_required
from bestvods.database import db
from bestvods.models import Platform

blueprint = flask.Blueprint('platforms', __name__, template_folder='templates')


@blueprint.route('/', methods=['GET'])
def root():
    term = flask.request.args['term'] + '%' if 'term' in flask.request.args else '%'
    platforms = Platform.query.filter(Platform.name.like(term)).limit(50)

    if utils.accepts_json(flask.request):
        return flask.Response(json.dumps([g.name for g in platforms]), mimetype='application/json')
    else:
        strings = [p.name + ": " + p.description for p in platforms]
        return flask.render_template('_list.html', list_header='Platforms', items=strings)


class AddPlatformForm(wtforms.Form):
    name = wtforms.StringField('Name', [validators.DataRequired(), validators.Length(max=255)])
    description = wtforms.StringField('Description', [validators.DataRequired(), validators.Length(max=2048)])


@blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddPlatformForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        try:
            platform = Platform(form.name.data, form.description.data)
            db.session.add(platform)
            db.session.commit()
            flask.flash('Inserted platform: ' + platform.name)
            return flask.redirect(flask.url_for('platforms.add'))
        except sqlalchemy.exc.IntegrityError:
            flask.flash('Platform ' + platform.name + ' already exists')
            return flask.redirect(flask.url_for('platforms.add'))
    return flask.render_template('_resource_add.html',
                                 resource_name='Platform',
                                 fields=[form.name, form.description])