import bestvods.queries as queries
import bestvods.validators
import datetime
import wtforms
import wtforms.validators as validators

from bestvods.database import db


class HHMMSSForm(wtforms.Form):
    hours = wtforms.IntegerField('Hours', [validators.number_range(min=0, max=24 * 7)])
    minutes = wtforms.IntegerField('Minutes', [validators.number_range(min=0, max=60)])
    seconds = wtforms.IntegerField('Seconds', [validators.number_range(min=0, max=60)])

    def validate(self):
        if not super().validate():
            return False

        if self.total_seconds <= 0:
            self.seconds.errors.append('Runs at least take a second!')
            return False
        else:
            return True

    @property
    def total_seconds(self):
        return self.hours.data * 60 * 60 + self.minutes.data * 60 + self.seconds.data


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


class RunnersForm(wtforms.Form):
    runner_exists = bestvods.validators.SatisfiesQuery(db, queries.participant_exists, "No such runner!")
    runners = wtforms.FieldList(wtforms.StringField('Runner', [validators.DataRequired(), runner_exists]),
                                min_entries=1)
    add_runner = wtforms.SubmitField()
    remove_runner = wtforms.SubmitField()

    def validate(self):
        if not super().validate():
            return False

        if len(self.runners.data) > len(frozenset(self.runners.data)):
            self.runners.errors.append('Runners must be unique!')
            return False
        else:
            return True


class CommentatorsForm(wtforms.Form):
    commentator_exists = bestvods.validators.SatisfiesQuery(db, queries.participant_exists, "No such commentator!")
    commentators = wtforms.FieldList(wtforms.StringField('Commentator',
                                                         [validators.DataRequired(), commentator_exists]))
    add_commentator = wtforms.SubmitField()
    remove_commentator = wtforms.SubmitField()

    def validate(self):
        if not super().validate():
            return False

        if len(self.commentators.data) > len(frozenset(self.commentators.data)):
            self.commentators.errors.append('Commentators must be unique!')
            return False
        else:
            return True


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