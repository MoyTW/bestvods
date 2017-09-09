import flask

from bestvods.database import db
from bestvods.models import Vod, UserRec

blueprint = flask.Blueprint('index', __name__, template_folder='templates')

INDEX_RESULT_LIMIT = 2


@blueprint.route('/', methods=['GET'])
def root():
    # Want the n most common VoDs from user recs
    vod_counts = db.session.query(Vod, db.func.count(UserRec.id).label("count"))\
        .join(UserRec)\
        .group_by(UserRec.vod_id)\
        .limit(INDEX_RESULT_LIMIT)\
        .all()
    popular_info = [{"count": row[1],
                     "game": row[0].game.name_release_year,
                     "platform": row[0].platform.name,
                     "category": row[0].category.name,
                     "event": row[0].event[0].name if len(row[0].event) > 0 else "",
                     "runners": [runner.handle for runner in row[0].runners],
                     "time": row[0].run_time_seconds}
                    for row in vod_counts]
    return flask.render_template('index.html', popular_info=popular_info)
