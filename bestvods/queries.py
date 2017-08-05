import flask_sqlalchemy as f_alchemy
import sqlalchemy as alchemy
import sqlalchemy.exc as alchemy_exc
import datetime


def parse_name_release_year(name_release_year):
    return [name_release_year[:-6].strip(), int(name_release_year[-6:].strip('()'))]



_insert_platform_text = alchemy.text("insert into platform values (:name, :description)")


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


def game_exists(db: f_alchemy.SQLAlchemy, name_release_year):
    try:
        release_year = int(name_release_year[-6:].strip('()'))
    except ValueError:
        return False

    result = db.engine.execute('select count(*) from game where name=:name and release_year=:release_year',
                               name=name_release_year[:-6].strip(),
                               release_year=release_year)
    return result.first()[0]


def category_exists(db: f_alchemy.SQLAlchemy, category):
    return db.engine.execute('select count(*) from category where name=:name', name=category).first()[0]

_insert_category_text = alchemy.text("insert into category values "
                                     "(null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, :name, :description, :game_id)")


def insert_category(db: f_alchemy.SQLAlchemy, game_id: int, name, description):
    try:
        db.engine.execute(_insert_category_text,
                          game_id=game_id,
                          name=name,
                          description=description)
        return True
    except alchemy_exc.IntegrityError:
        return False


def platform_exists(db: f_alchemy.SQLAlchemy, platform):
    return db.engine.execute('select count(*) from platform where name=:name', name=platform).first()[0]


def insert_platform(db: f_alchemy.SQLAlchemy, name, description):
    try:
        db.engine.execute(_insert_platform_text,
                          name=name,
                          description=description)
        return True
    except alchemy_exc.IntegrityError:
        return False


# This one will wait a bit
def insert_tag(db: f_alchemy.SQLAlchemy, name, description):
    pass

_insert_event_text = alchemy.text("insert into event values (:name, :start_date, :end_date, :description)")


def insert_event(db: f_alchemy.SQLAlchemy, name, start_date: datetime.date, end_date: datetime.date, description):
    try:
        db.engine.execute(_insert_event_text,
                          name=name,
                          start_date=start_date,
                          end_date=end_date,
                          description=description)
        return True
    except alchemy_exc.IntegrityError:
        return False


def select_participant(db: f_alchemy.SQLAlchemy, handle):
    return db.engine.execute('select * from participant where handle=:handle', handle=handle).first()


def participant_exists(db: f_alchemy.SQLAlchemy, handle):
    return db.engine.execute('select count(*) from participant where handle=:handle', handle=handle).first()[0]


_insert_participant_text = alchemy.text("insert into participant values (null, :handle, :stream_url)")


def insert_participant(db: f_alchemy.SQLAlchemy, handle, stream_url):
    try:
        db.engine.execute(_insert_participant_text, handle=handle, stream_url=stream_url)
        return True
    except alchemy_exc.IntegrityError:
        return False

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


vod_search = """
select vod.id, vod.run_time_seconds, vod.platform_name, vod.completed_date, game.name,
    (select group_concat(participant.handle, ', ') from vods_runners
     join participant on vods_runners.participant_id=participant.id
     where vod.id=vods_runners.vod_id
     group by vods_runners.vod_id) as runners,
    (select group_concat(participant.handle, ', ') from vods_commentators
     join participant on vods_commentators.participant_id=participant.id
     where vod.id=vods_commentators.vod_id
     group by vods_commentators.vod_id) as commentators
from vod
join game on vod.game_id=game.id
where (vod.game_id=:game_id or :game_id is null) and
    (exists (select * from vods_runners where participant_id=:runner_id) or :runner_id is null) and
    (exists (select * from vods_commentators where participant_id=:commentator_id) or :commentator_id is null)
limit :limit
"""


def search_vod(db: f_alchemy, game_name_release_year, runner_handle, commentator_handle, limit=50):
    game = _select_game(db, game_name_release_year)
    if game is None:
        game_id = None
    else:
        game_id = game['id']

    runner = select_participant(db, runner_handle)
    runner_id = None if runner is None else runner['id']
    commentator = select_participant(db, commentator_handle)
    commentator_id = None if commentator is None else commentator['id']

    return db.engine.execute(vod_search, game_id=game_id, runner_id=runner_id, commentator_id=commentator_id,
                             limit=limit).fetchall()
