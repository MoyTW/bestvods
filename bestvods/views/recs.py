import flask

from bestvods.models import UserRec


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
