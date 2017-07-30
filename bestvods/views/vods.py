import bestvods.queries as queries
import bestvods.validators
import datetime
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


class DateForm(wtforms.Form):
    year = wtforms.IntegerField('Year', [validators.DataRequired(),
                                         validators.number_range(min=1962, max=datetime.date.today().year)])
    month = wtforms.IntegerField('Month', [validators.DataRequired(), validators.number_range(min=1, max=12)])
    day = wtforms.IntegerField('Day', [validators.DataRequired(), validators.number_range(min=1, max=31)])

    def validate(self):
        if not super().validate():
            return False

        try:
            datetime.date(year=self.year.data, month=self.month.data, day=self.day.data)
            return True
        except ValueError:
            self.day.errors.append('Day ' + str(self.day.data) + ' is not a valid day for ' + str(self.month.data) +
                                   '!')
            return False

    @property
    def date(self) -> datetime.date:
        return datetime.date(year=self.year.data, month=self.month.data, day=self.day.data)


class HHMMSSForm(wtforms.Form):
    hours = wtforms.IntegerField('Hours', [validators.DataRequired(), validators.number_range(min=0, max=24 * 7)])
    minutes = wtforms.IntegerField('Minutes', [validators.DataRequired(), validators.number_range(min=0, max=60)])
    seconds = wtforms.IntegerField('Seconds', [validators.DataRequired(), validators.number_range(min=0, max=60)])

    @property
    def seconds(self):
        return self.hours * 60 * 60 + self.minutes * 60 + self.seconds


class RunnersForm(wtforms.Form):
    runner_exists = bestvods.validators.SatisfiesQuery(db, queries.participant_exists, "No such runner!")
    runners = wtforms.FieldList(wtforms.StringField('Runner', [validators.DataRequired(), runner_exists]),
                                min_entries=1)
    add_runner = wtforms.SubmitField()
    remove_runner = wtforms.SubmitField()


class CommentatorsForm(wtforms.Form):
    commentator_exists = bestvods.validators.SatisfiesQuery(db, queries.participant_exists, "No such commentator!")
    commentators = wtforms.FieldList(wtforms.StringField('Commentator',
                                                         [validators.DataRequired(), commentator_exists]))
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
    date_completed = wtforms.FormField(DateForm)
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
