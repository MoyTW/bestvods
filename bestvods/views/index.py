import datetime
import flask
import flask_table

from bestvods.database import db
from bestvods.models import Vod, UserRec
from typing import List

blueprint = flask.Blueprint('index', __name__, template_folder='templates')

INDEX_RESULT_LIMIT = 5


class SecondsCol(flask_table.Col):
    def td_format(self, content: int):
        delta = datetime.timedelta(seconds=content)
        return str(delta)


class VodCountsTable(flask_table.Table):
    count = flask_table.Col("Recommenders")
    game = flask_table.LinkCol("Game",
                               endpoint='games.name_release_year_handler',
                               attr='game.name_release_year',
                               url_kwargs=dict(name_release_year='game.name_release_year'))
#    platform = flask_table.LinkCol("Platform")
#    category = CategoryCol("Category")
#    event = EventCol("Event")
#    runners = RunnersCol("Runners")
    run_time_seconds = SecondsCol("Time")


@blueprint.route('/', methods=['GET'])
def root():
    # Want the n most common VoDs from user recs
    vod_counts = db.session.query(Vod, db.func.count(UserRec.id).label("count"))\
        .join(UserRec)\
        .group_by(UserRec.vod_id)\
        .limit(INDEX_RESULT_LIMIT)\
        .all()
    table_rows = []
    for row in vod_counts:
        table_row = row[0].__dict__
        table_row['count'] = row[1]
        table_rows.append(row[0])
    table = VodCountsTable(table_rows)

    newest_results = UserRec.query.order_by(UserRec.timestamp_created.desc()).limit(INDEX_RESULT_LIMIT)
    newest_info = [{"user": row.user.username,
                    "recommended_on": row.timestamp_created.date(),
                    "vod_description": row.vod.description,
                    "user_description": row.description,
                    "tags": [tag.name for tag in row.tags]}
                   for row in newest_results]

    return flask.render_template('index.html', newest_info=newest_info, table=table)
