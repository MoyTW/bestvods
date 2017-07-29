import bestvods.queries as queries
import bestvods.validators
import flask
import wtforms
import wtforms.validators as validators

from flask_security import login_required
from bestvods.database import db


blueprint = flask.Blueprint('vods', __name__, template_folder='templates')


def query_vod(vod_id: int):
    select_game = 'select id, game_name, game_release_year, platform_name, category_name from vod where id=:id'
    select_runners = 'select participant.handle from participant ' \
                     'join vods_runners on participant.id=vods_runners.participant_id ' \
                     'where vod_id=:id'
    select_commentators = 'select participant.handle from participant ' \
                          'join vods_commentators on participant.id=vods_commentators.participant_id ' \
                          'where vod_id=:id'
    vod = db.engine.execute(select_game, id=vod_id).first()
    participants = db.engine.execute(select_runners, id=vod_id).fetchall()
    commentators = db.engine.execute(select_commentators, id=vod_id).fetchall()
    return str(vod) + ' Runner(s): ' + str(participants) + ' Commentators: ' + str(commentators)


@blueprint.route('/', methods=['GET'])
def root():
    all_ids = db.engine.execute('select id from vod').fetchall()
    strings = [query_vod(vod_id[0]) for vod_id in all_ids]
    return flask.render_template('_list.html', list_header='VoDs', items=strings)


class HHMMSSForm(wtforms.Form):
    hours = wtforms.IntegerField('Hours', [validators.DataRequired(), validators.number_range(min=0, max=24 * 7)])
    minutes = wtforms.IntegerField('Minutes', [validators.DataRequired(), validators.number_range(min=0, max=60)])
    seconds = wtforms.IntegerField('Seconds', [validators.DataRequired(), validators.number_range(min=0, max=60)])


class RunnersForm(wtforms.Form):
    runners = wtforms.FieldList(wtforms.StringField('Runner', [validators.DataRequired()]), min_entries=1)
    add_runner = wtforms.SubmitField()
    remove_runner = wtforms.SubmitField()


class CommentatorsForm(wtforms.Form):
    commentators = wtforms.FieldList(wtforms.StringField('Commentator', [validators.DataRequired()]))
    add_commentator = wtforms.SubmitField()
    remove_commentator = wtforms.SubmitField()


class AddVoDForm(wtforms.Form):
    # This is kind of silly-looking, I admit. Just, like, formatting-wise.
    game = wtforms.StringField('Game',
                               [validators.DataRequired(),
                                validators.Length(max=256+7),
                                bestvods.validators.SatisfiesQuery(db,
                                                                   queries.game_exists,
                                                                   "I don't know this game!")],
                               id='game_autocomplete')
    platform = wtforms.StringField('Platform',
                                   [validators.DataRequired(),
                                    validators.Length(max=256),
                                    bestvods.validators.SatisfiesQuery(db,
                                                                       queries.platform_exists,
                                                                       "I don't know this platform!")],
                                   id='platform_autocomplete')
    category = wtforms.StringField('Category',
                                   [validators.DataRequired(),
                                    validators.Length(max=256),
                                    bestvods.validators.SatisfiesQuery(db,
                                                                       queries.category_exists,
                                                                       "I don't know this category!")],
                                   id='category_autocomplete')
    time = wtforms.FormField(HHMMSSForm)
    runners = wtforms.FormField(RunnersForm)
    commentators = wtforms.FormField(CommentatorsForm)
    add_vod = wtforms.SubmitField()


@blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddVoDForm(flask.request.form)

    # TODO: AJAX or JS frontend
    if flask.request.method == 'POST':
        if form.runners.add_runner.data:
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
            flask.flash('VALIDATED')
            print('VALIDATED')

    return flask.render_template('vod_add.html', form=form)
