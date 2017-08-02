import bestvods.forms as forms
import bestvods.queries as queries
import flask

from flask_security import login_required
from bestvods.database import db


blueprint = flask.Blueprint('vods', __name__, template_folder='templates')


def query_vod(vod_id: int):
    select_game = """
    select vod.id, game.name, platform_name, category.name from vod
    join game on vod.game_id=game.id
    join category on vod.category_id=category.id
    where vod.id=:id
    """
    select_links = 'select uri from vod_links where vod_id=:id'
    select_runners = 'select participant.handle from participant ' \
                     'join vods_runners on participant.id=vods_runners.participant_id ' \
                     'where vod_id=:id'
    select_commentators = 'select participant.handle from participant ' \
                          'join vods_commentators on participant.id=vods_commentators.participant_id ' \
                          'where vod_id=:id'
    vod = db.engine.execute(select_game, id=vod_id).first()
    links = db.engine.execute(select_links, id=vod_id).fetchall()
    participants = db.engine.execute(select_runners, id=vod_id).fetchall()
    commentators = db.engine.execute(select_commentators, id=vod_id).fetchall()
    return str(vod) + ' Link(s): ' + str(links) + ' Runner(s): ' + str(participants) + \
           ' Commentators: ' + str(commentators)


@blueprint.route('/', methods=['GET'])
def root():
    all_ids = db.engine.execute('select id from vod').fetchall()
    strings = [query_vod(vod_id[0]) for vod_id in all_ids]
    return flask.render_template('_list.html', list_header='VoDs', items=strings)


@blueprint.route('/search', methods=['GET', 'POST'])
def search():
    vod_strs = []
    form = forms.SearchVoDsForm(flask.request.form)

    if flask.request.method == 'POST':
        rows = queries.search_vod(db, form.game.data, form.runner.data, form.commentator.data)
        vod_strs = [str(row) for row in rows]
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
