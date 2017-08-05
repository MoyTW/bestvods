import flask

from bestvods.database import db


blueprint = flask.Blueprint('recs', __name__, template_folder='templates')


select_rec = """
select user.username, user_rec.id, game.name, event.name, vod.run_time_seconds, user_rec.description from user_rec
join event on vod.event_id=event.id
join user on user_rec.user_id=user.id
join vod on user_rec.vod_id=vod.id
join game on vod.game_id=game.id
where user_rec.id=:user_rec_id
"""

select_tags = """
select user_recs_tags.tag_name from user_recs_tags
where user_rec_id=:user_rec_id
"""


def query_rec(rec_id: int):
    rec = db.engine.execute(select_rec, user_rec_id=rec_id).first()
    tags = db.engine.execute(select_tags, user_rec_id=rec_id).fetchall()
    return str(rec) + ' Tag(s): ' + str(tags)


@blueprint.route('/', methods=['GET'])
def root():
    all_ids = db.engine.execute('select id from user_rec limit 50').fetchall()
    strings = [query_rec(rec_id[0]) for rec_id in all_ids]
    return flask.render_template('_list.html', list_header='Suggested', items=strings)