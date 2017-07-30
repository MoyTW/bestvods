import bestvods.queries as queries
import bestvods.validators
import bestvods.utils as utils
import flask
import json
import wtforms
import wtforms.validators as validators

from flask_security import login_required
from bestvods.database import db


blueprint = flask.Blueprint('participants', __name__, template_folder='templates')


# TODO: Magic numbers in autocomplete, page size
@blueprint.route('/', methods=['GET'])
def root():
    term = flask.request.args['term']+'%' if 'term' in flask.request.args else '%'

    if utils.accepts_json(flask.request):
        participants = db.engine.execute("select handle from participant where handle like :term limit 10",
                                         term=term).fetchall()
        return flask.Response(json.dumps([p.handle for p in participants]), mimetype='application/json')
    else:
        # Add pagination
        participants = db.engine.execute('select handle from participant where handle like :term limit 50',
                                         term=term).fetchall()
        strings = [p.handle for p in participants]
        return flask.render_template('_list.html', list_header='participants', items=strings)


class AddParticipantForm(wtforms.Form):
    participant_dne = bestvods.validators.SatisfiesQuery(db,
                                                         lambda d, h: not queries.participant_exists(db, h),
                                                         "Participant already exists!")
    handle = wtforms.StringField('Handle', [validators.DataRequired(), validators.Length(max=256), participant_dne])
    stream_url = wtforms.StringField('Stream URL', [validators.Length(max=512)])


@blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddParticipantForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        if queries.insert_participant(db, form.handle.data, form.stream_url.data):
            flask.flash('Inserted participant')
        else:
            flask.flash('participant already exists')
    return flask.render_template('_resource_add.html',
                                 resource_name='participant',
                                 fields=[form.handle, form.stream_url])