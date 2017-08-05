import bestvods.forms as forms
import bestvods.queries as queries
import flask

from flask_security import login_required
from bestvods.database import db
from bestvods.models import Vod, Game


blueprint = flask.Blueprint('vods', __name__, template_folder='templates')


@blueprint.route('/', methods=['GET'])
def root():
    vods = Vod.query.limit(50).all()
    strings = [[(k, v) for k, v in vod.__dict__.items() if not k.startswith('_')] for vod in vods]
    return flask.render_template('_list.html', list_header='VoDs', items=strings)


@blueprint.route('/search', methods=['GET', 'POST'])
def search():
    vod_strs = []
    form = forms.SearchVoDsForm(flask.request.form)

    if flask.request.method == 'POST' and form.validate():
        query = Vod.query;
        if form.game.data is not None:
            name, release_year = Game.parse_name_release_year(form.game.data)
            query = query.filter(Vod.game.has(name=name, release_year=release_year))
        # TODO: Refine search
        if form.runner.data is not None:
            print('TODO Runner')
        if form.commentator.data is not None:
            print('TODO Commentator')

        rows = query.all()
        vod_strs = [[(k, v) for k, v in vod.__dict__.items() if not k.startswith('_')] for vod in rows]
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
            queries.insert_vod(db, form.links.links.data, form.game.data, form.platform.data, form.category.data,
                               form.time.total_seconds, form.date_completed.date, form.runners.runners.data,
                               form.commentators.commentators.data)
            return flask.redirect(flask.url_for('vods.add'))

    return flask.render_template('vod_add.html', form=form)
