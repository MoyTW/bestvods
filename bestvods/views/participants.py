import bestvods.utils as utils
import flask
import json
import sqlalchemy.exc
import wtforms
import wtforms.validators as validators

from flask_security import login_required
from bestvods.database import db
from bestvods.models import Participant


blueprint = flask.Blueprint('participants', __name__, template_folder='templates')


# TODO: Magic numbers in autocomplete, page size
@blueprint.route('/', methods=['GET'])
def root():
    term = flask.request.args['term']+'%' if 'term' in flask.request.args else '%'
    participants = Participant.query.filter(Participant.handle.like(term)).limit(50)

    if utils.accepts_json(flask.request):
        return flask.Response(json.dumps([p.handle for p in participants]), mimetype='application/json')
    else:
        strings = [p.handle for p in participants]
        return flask.render_template('_list.html', list_header='participants', items=strings)


class AddParticipantForm(wtforms.Form):
    handle = wtforms.StringField('Handle', [validators.DataRequired(),
                                            validators.Length(max=256)])
    stream_url = wtforms.StringField('Stream URL', [validators.Length(max=512)])


@blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddParticipantForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        try:
            participant = Participant(form.handle.data, form.stream_url.data)
            db.session.add(participant)
            db.session.commit()
            flask.flash('Inserted participant: ' + participant.handle)
            return flask.redirect(flask.url_for('participants.add'))
        except sqlalchemy.exc.IntegrityError:
            flask.flash('Participant ' + form.handle.data + ' already exists')
            return flask.redirect(flask.url_for('participants.add'))
    return flask.render_template('_resource_add.html',
                                 resource_name='participant',
                                 fields=[form.handle, form.stream_url])