import bestvods.forms as forms
import bestvods.utils as utils
import flask
import json
import sqlalchemy.exc

from flask_security import login_required
from bestvods.database import db
from bestvods.models import Tag

blueprint = flask.Blueprint('tags', __name__, template_folder='templates')


@blueprint.route('/', methods=['GET'])
def root():
    term = flask.request.args['term'] + '%' if 'term' in flask.request.args else '%'
    tags = Tag.query.filter(Tag.name.like(term)).limit(50)

    if utils.accepts_json(flask.request):
        return flask.Response(json.dumps([g.name for g in tags]), mimetype='application/json')
    else:
        strings = [p.name + ": " + p.description for p in tags]
        return flask.render_template('_list.html', list_header='tags', items=strings)


@blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = forms.AddTagForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        try:
            tag = Tag(form.name.data, form.description.data)
            db.session.add(tag)
            db.session.commit()
            flask.flash('Inserted tag: ' + tag.name)
            return flask.redirect(flask.url_for('tags.add'))
        except sqlalchemy.exc.IntegrityError:
            flask.flash('tag ' + form.name.data + ' already exists')
            return flask.redirect(flask.url_for('tags.add'))
    return flask.render_template('_resource_add.html',
                                 resource_name='tag',
                                 fields=[form.name, form.description, form.add_tag])
