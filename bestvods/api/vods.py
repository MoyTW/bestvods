import bestvods.utils as utils
import flask
import sqlalchemy.orm as orm
from bestvods.models import Vod


blueprint = flask.Blueprint('api_vods', __name__, template_folder='templates')


def vod_string(vod: Vod):
    return ", ".join(['id: ' + str(vod.id),
                      'game: ' + vod.game.name,
                      'event: ' + vod.event[0].name if len(vod.event) > 0 else 'No Event',
                      'runners: [' + ','.join([p.handle for p in vod.runners]) + ']',
                      'commentators: [' + ','.join([p.handle for p in vod.commentators]) + ']',
                      'links: [' + ' : '.join(l.url for l in vod.links) + ']'])


@blueprint.route('/', methods=['GET'])
def get_root():
    # TODO: Limit 50 should not be hard-coded
    vods = Vod.query.options(orm.subqueryload('game'),
                             orm.subqueryload('platform'),
                             orm.subqueryload('category')
                             ).order_by(Vod.id).limit(50).all()
    return flask.Response(utils.custom_dumps(vods), mimetype='application/json')