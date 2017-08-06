import bestvods.forms as forms
import bestvods.utils as utils
import flask
import json
import sqlalchemy.exc

from flask_security import login_required
from bestvods.database import db
from bestvods.models import Event

blueprint = flask.Blueprint('events', __name__, template_folder='templates')


@blueprint.route('/', methods=['GET'])
def root():
    term = flask.request.args['term'] + '%' if 'term' in flask.request.args else '%'
    events = Event.query.filter(Event.name.like(term)).limit(50)

    if utils.accepts_json(flask.request):
        return flask.Response(json.dumps([g.name for g in events]), mimetype='application/json')
    else:
        strings = [p.name + ": " + p.description for p in events]
        return flask.render_template('_list.html', list_header='events', items=strings)


@blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = forms.AddEventForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        try:
            event = Event(form.name.data, form.start_date.date, form.end_date.date, form.description.data)
            db.session.add(event)
            db.session.commit()
            flask.flash('Inserted event: ' + event.name)
            return flask.redirect(flask.url_for('events.add'))
        except sqlalchemy.exc.IntegrityError:
            flask.flash('event ' + form.name.data + ' already exists')
            return flask.redirect(flask.url_for('events.add'))
    return flask.render_template('_resource_add.html',
                                 resource_name='event',
                                 fields=[form.name, form.start_date, form.end_date, form.description, form.add_event])
