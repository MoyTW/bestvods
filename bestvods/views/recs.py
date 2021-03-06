import bestvods.forms as forms
import flask
import sqlalchemy.exc

from bestvods.database import db
from bestvods.models import UserRec, Vod
from flask_security import login_required, current_user


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


@blueprint.route('/list/<string:username>/', methods=['GET'])
def list_username(username):
    user_recs = UserRec.query.filter(UserRec.user.has(username=username)).limit(50)
    strings = [[rec.user.username,
                rec.vod.game.name,
                rec.vod.event[0].name if len(rec.vod.event) > 0 else 'No Event',
                rec.description,
                'tags: ' + str([tag.name for tag in rec.tags])]
               for rec in user_recs]
    return flask.render_template('_list.html', list_header='Suggested', items=strings)


@blueprint.route('/add/', methods=['GET', 'POST'])
@login_required
def add():
    form = forms.SearchVoDsForm(flask.request.form)

    if flask.request.method == 'POST' and form.validate():
        rows = Vod.query_search(form.game.data, form.runner.data,
                                form.commentator.data, form.event.data)
        vod_dicts = [{'desc': str(vod), 'href': flask.url_for('recs.add_vod', vod_id=vod.id)} for vod in rows]
        return flask.render_template('rec_add.html', form=form, vod_dicts=vod_dicts)

    return flask.render_template('rec_add.html', form=form)


@blueprint.route('/add/<int:vod_id>', methods=['GET', 'POST'])
@login_required
def add_vod(vod_id):
    vod = Vod.query.filter_by(id=vod_id).first()
    if vod is None:
        flask.abort(404)

    form = forms.AddUserRecVodForm(flask.request.form)

    if flask.request.method == 'POST':
        if form.tags.add_tag.data:
            form.tags.tags.append_entry()
        elif form.tags.remove_tag.data:
            form.tags.tags.pop_entry()

        elif form.validate():
            try:
                username = current_user.username
                user_rec = UserRec.create_with_related(username, vod_id, form.description.data, form.tags.tags.data)
                db.session.add(user_rec)
                db.session.commit()
                flask.flash('Inserted Rec: ' + str(user_rec.id))
                return flask.redirect(flask.url_for('recs.add'))
            except sqlalchemy.exc.IntegrityError:
                flask.flash('You already recommended vod ' + str(vod_id))
                return flask.redirect(flask.url_for('recs.add'))

    return flask.render_template('rec_add_vod.html', form=form, vod_str=str(vod))
