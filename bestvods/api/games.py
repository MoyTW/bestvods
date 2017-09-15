import bestvods.utils as utils
import flask
import json
import sqlalchemy.exc
import wtforms
import wtforms.validators as validators

from flask_security import login_required
from bestvods.database import db
from bestvods.models import Game, Category


blueprint = flask.Blueprint('api_games', __name__, template_folder='templates')


@blueprint.route('/', methods=['GET'])
def get_root():
    term = flask.request.args['term']+'%' if 'term' in flask.request.args else '%'
    # TODO: Add pagination
    games = Game.query.filter(Game.name.like(term)).limit(50).all()
    return flask.Response(utils.custom_dumps(games), mimetype='application/json')


@blueprint.route('/<int:game_id>/', methods=['GET'])
def get_game_id(game_id):
    game = Game.query.filter_by(id=game_id).first()
    if game is None:
        flask.abort(404)
    else:
        return flask.Response(utils.custom_dumps(game), mimetype='application/json')
