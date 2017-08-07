import bestvods.forms as forms
import flask
import sqlalchemy.exc

from bestvods.database import db
from bestvods.models import UserRec, Tag
from flask_security import login_required


blueprint = flask.Blueprint('recs', __name__, template_folder='templates')


@blueprint.route('/', methods=['GET'])
def root():
    user_recs = UserRec.query.limit(50)
    strings = [[rec.user.username,
                rec.vod.game.name,
                rec.vod.event[0].name if len(rec.vod.event) > 0 else 'No Event',
                rec.description,
                'tags: ' + str([tag.name for tag in rec.tags])]
               for rec in user_recs]
    return flask.render_template('_list.html', list_header='Suggested', items=strings)


@blueprint.route('/<string:username>/', methods=['GET'])
def username_root(username):
    user_recs = UserRec.query.filter(UserRec.user.has(username=username)).limit(50)
    strings = [[rec.user.username,
                rec.vod.game.name,
                rec.vod.event[0].name if len(rec.vod.event) > 0 else 'No Event',
                rec.description,
                'tags: ' + str([tag.name for tag in rec.tags])]
               for rec in user_recs]
    return flask.render_template('_list.html', list_header='Suggested', items=strings)


@blueprint.route('/<string:username>/add', methods=['GET', 'POST'])
@login_required
def username_add(username):
    form = forms.AddUserRecForm(flask.request.form)

    if flask.request.method == 'POST':
        if form.tags.add_tag.data:
            form.tags.tags.append_entry()
        elif form.tags.remove_tag.data:
            form.tags.tags.pop_entry()

        elif form.validate():
            try:
                user_rec = UserRec.create_with_related(username, form.vod_id.data, form.description.data,
                                                       form.tags.tags.data)
                db.session.add(user_rec)
                db.session.commit()
                flask.flash('Inserted Rec: ' + str(user_rec.id))
                return flask.redirect(flask.url_for('recs.username_add', username=username))
            except sqlalchemy.exc.IntegrityError:
                flask.flash('You already recommended vod ' + str(form.vod_id.data))
                return flask.redirect(flask.url_for('recs.username_add', username=username))
    return flask.render_template('_resource_add.html',
                                 resource_name='event',
                                 fields=[form.vod_id, form.description, form.tags, form.add_user_rec])
