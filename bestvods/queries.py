import flask_sqlalchemy as f_alchemy
import sqlalchemy as alchemy
import datetime


def _select_game(db: f_alchemy.SQLAlchemy, name_release_year):
    try:
        release_year = int(name_release_year[-6:].strip('()'))
    except ValueError:
        return None

    result = db.engine.execute('select id, added_at, name, release_year, description from game '
                               'where name=:name and release_year=:release_year',
                               name=name_release_year[:-6].strip(),
                               release_year=release_year)
    return result.first()


_insert_vod_text = alchemy.text("""
insert into vod values(null, CURRENT_TIMESTAMP, :run_time_seconds, :completed_date, :game_id, :platform_name,
                       (select id from category where game_id=:game_id and name=:category_name));
""")


def insert_vod(db: f_alchemy.SQLAlchemy, links, game_name_release_year, platform_name, category_name, run_time_seconds,
               completed_date: datetime.date, runner_handles, commentator_handles):
    game = _select_game(db, game_name_release_year)
    if game is None:
        return False

    with db.engine.begin() as transaction:
        transaction.execute(_insert_vod_text, run_time_seconds=run_time_seconds, completed_date=completed_date,
                            game_id=game['id'], platform_name=platform_name, category_name=category_name)
        vod_id = transaction.execute('select last_insert_rowid()').first()[0]
        for url in links:
            transaction.execute('insert into vod_links values (:url, :vod_id)', url=url, vod_id=vod_id)
        for handle in runner_handles:
            sql = 'insert into vods_runners values (:vod_id, (select id from participant where handle=:handle))'
            transaction.execute(sql, vod_id=vod_id, handle=handle)
        for handle in commentator_handles:
            sql = 'insert into vods_commentators values (:vod_id, (select id from participant where handle=:handle))'
            transaction.execute(sql, vod_id=vod_id, handle=handle)

    return True
