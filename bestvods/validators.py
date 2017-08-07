import wtforms

from bestvods.models import Game, Platform, Participant, Event


class _RowExists:
    def __init__(self, allow_empty=False, message=None):
        self.allow_empty = allow_empty
        if not message:
            self.message = u"There's no record of this item!"
        else:
            self.message = message

    def _row_missing(self, form, field):
        raise NotImplementedError("This method is should be implemented in the child class!")

    def __call__(self, form, field):
        if (not (self.allow_empty and (field.data is None or field.data == ''))) and self._row_missing(form, field):
            raise wtforms.ValidationError(self.message)


class GameExists(_RowExists):
    def __init__(self, allow_empty=False, message=u"Game not found!"):
        super().__init__(allow_empty=allow_empty, message=message)

    def _row_missing(self, form, field):
        name, release_year = Game.parse_name_release_year(field.data)
        return Game.query.filter_by(name=name, release_year=release_year).first() is None


class PlatformExists(_RowExists):
    def __init__(self, allow_empty=False, message=u"Platform not found!"):
        super().__init__(allow_empty=allow_empty, message=message)

    def _row_missing(self, form, field):
        return Platform.query.filter_by(name=field.data).first() is None


class CategoryExists(_RowExists):
    def __init__(self, game_field_name, allow_empty=False, message=u"Category not found for game!"):
        super().__init__(allow_empty=allow_empty, message=message)

        self.game_field_name = game_field_name

    def _row_missing(self, form, field):
        game_field = form._fields.get(self.game_field_name)
        name, release_year = Game.parse_name_release_year(game_field.data)
        game = Game.query.filter_by(name=name, release_year=release_year).first()
        return game is None or game.categories.filter_by(name=field.data).first() is None


class ParticipantExists(_RowExists):
    def __init__(self, allow_empty=False, message=u"Runner/commentator not found!"):
        super().__init__(allow_empty=allow_empty, message=message)

    def _row_missing(self, form, field):
        return Participant.query.filter_by(handle=field.data).first() is None


class EventExists(_RowExists):
    def __init__(self, allow_empty=False, message=u"Event not found!"):
        super().__init__(allow_empty=allow_empty, message=message)

    def _row_missing(self, form, field):
        return Event.query.filter_by(name=field.data).first() is None
