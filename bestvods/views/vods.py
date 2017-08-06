import bestvods.forms as forms
import flask
import sqlalchemy.exc

from flask_security import login_required
from bestvods.database import db
from bestvods.models import Vod, Game


blueprint = flask.Blueprint('vods', __name__, template_folder='templates')


def vod_string(vod: Vod):
    return ", ".join(['id: ' + str(vod.id),
                      'game: ' + vod.game.name,
                      'event: ' + vod.event[0].name if len(vod.event) > 0 else 'No Event',
                      'runners: [' + ','.join([p.handle for p in vod.runners]) + ']',
                      'commentators: [' + ','.join([p.handle for p in vod.commentators]) + ']',
                      'links: [' + ' : '.join(l.url for l in vod.links) + ']'])


@blueprint.route('/', methods=['GET'])
def root():
    vods = Vod.query.limit(50).all()
    strings = [vod_string(vod) for vod in vods]
    return flask.render_template('_list.html', list_header='VoDs', items=strings)


@blueprint.route('/search', methods=['GET', 'POST'])
def search():
    vod_strs = []
    form = forms.SearchVoDsForm(flask.request.form)

    if flask.request.method == 'POST' and form.validate():
        query = Vod.query
        if form.game.data != '':
            name, release_year = Game.parse_name_release_year(form.game.data)
            query = query.filter(Vod.game.has(name=name, release_year=release_year))
        # TODO: Refine search
        if form.runner.data != '':
            print('TODO Runner')
        if form.commentator.data != '':
            print('TODO Commentator')

        rows = query.all()
        vod_strs = [vod_string(vod) for vod in rows]
        return flask.render_template('vod_search.html', form=form, vod_strs=vod_strs)

    return flask.render_template('vod_search.html', form=form, vod_strs=vod_strs)


@blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = forms.AddVoDForm(flask.request.form)

    # TODO: AJAX or JS frontend
    if flask.request.method == 'POST':
        if form.links.add_link.data:
            form.links.links.append_entry()
        elif form.links.remove_link.data:
            if len(form.links.links.entries) > 1:
                form.links.links.pop_entry()

        elif form.runners.add_runner.data:
            form.runners.runners.append_entry()
        elif form.runners.remove_runner.data:
            if len(form.runners.runners.entries) > 1:
                form.runners.runners.pop_entry()

        elif form.commentators.add_commentator.data:
            form.commentators.commentators.append_entry()
        elif form.commentators.remove_commentator.data:
            if len(form.commentators.commentators.entries) > 0:
                form.commentators.commentators.pop_entry()

        elif form.validate() and form.add_vod.data:
            try:
                vod = Vod.create_with_related(
                    form.game.data, form.platform.data, form.category.data, form.time.total_seconds,
                    form.date_completed.date, None, form.links.links.data, form.runners.runners.data,
                    form.commentators.commentators.data)
                db.session.add(vod)
                db.session.commit()
                return flask.redirect(flask.url_for('vods.add'))
            except sqlalchemy.exc.IntegrityError:
                flask.flash('A vod for URL one or more of the URLs already exists!')

    return flask.render_template('vod_add.html', form=form)
