import datetime
import json
import sqlite3
import itertools


def take(n, iterable):
    return list(itertools.islice(iterable, n))

with open('./resources/gdq-vods-agdq-2016-runData.json') as data_file:
    data = json.load(data_file)

conn = sqlite3.connect('./dev/bestvods.db')
vods = sorted([[item[0], item[1]] for item in data.items()], key=lambda kv: kv[0])

# Insert event
event_name = vods[0][1]['event']['name']
event_row = conn.execute('select id from event where name=?', [event_name]).fetchone()
if event_row is None:
    vod_times = [datetime.datetime.utcfromtimestamp(vod[1]['start_time']).date() for vod in vods]
    params = [event_name, min(vod_times), max(vod_times), event_name]
    conn.execute('insert into event values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?, ?, ?)', params)
    print('Inserted EVENT: ' + str(params))
    event_id = conn.execute('select last_insert_rowid()').fetchone()[0]
else:
    raise ValueError('You have already processed this file!')

for name, vod_json in vods:
    game_name = vod_json['game']['name']
    game_year = vod_json['game']['year']

    print(game_name + ': ' + str(game_year))

    # Insert game
    game_row = conn.execute('select id from game where name=? and release_year=?', [game_name, game_year]).fetchone()
    if game_row is None:
        params = [game_name, game_year, game_name + ' was a game released in ' + str(game_year)]
        conn.execute('insert into game values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?, ?)', params)
        print('    Inserted GAME: ' + str(params))
        game_id = conn.execute('select last_insert_rowid()').fetchone()[0]
    else:
        game_id = game_row[0]

    # Insert category for game
    category_name = vod_json['category']
    category_row = conn.execute('select category.id from category '
                                'join game on category.game_id=game.id '
                                'where category.name=? and game.id=?',
                                [category_name, game_id]).fetchone()
    if category_row is None:
        params = [category_name, 'Category Placeholder Description', game_id]
        conn.execute('insert into category values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?, ?)', params)
        print('    Inserted CATEGORY ' + str(params))
        category_id = conn.execute('select last_insert_rowid()').fetchone()[0]
    else:
        category_id = category_row[0]

    # Insert platform
    platform_name = vod_json['game']['platform']['name']
    platform_row = conn.execute('select id from platform where name=?', [platform_name]).fetchone()
    if platform_row is None:
        params = [platform_name, 'Platform Placeholder Description']
        conn.execute('insert into platform values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?)', params)
        print('    Inserted PLATFORM ' + str(params))
        platform_id = conn.execute('select last_insert_rowid()').fetchone()[0]
    else:
        platform_id = platform_row[0]

    # Insert runners
    runner_ids = []
    for runner in vod_json['runners']:
        runner_name = runner['name']
        runner_row = conn.execute('select id from participant where handle=?', [runner_name]).fetchone()
        if runner_row is None:
            params = [runner_name, 'https://twitch.tv/' + runner['twitch'] if 'twitch' in runner else '']
            conn.execute('insert into participant values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?)', params)
            print('    Inserted PARTICIPANT ' + str(params))
            runner_ids.append(conn.execute('select last_insert_rowid()').fetchone()[0])
        else:
            runner_ids.append(runner_row[0])

    # Insert VoD
    hours, minutes, seconds = vod_json['duration'].split(':')
    run_time_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
    end_date = datetime.datetime.utcfromtimestamp(vod_json['start_time']).date()

    params = [run_time_seconds, end_date, game_id, platform_id, category_id]
    conn.execute('insert into vod values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)', params)
    print('    Inserted VOD ' + str(params))
    vod_id = conn.execute('select last_insert_rowid()').fetchone()[0]

    # Vod->Event
    conn.execute('insert into vods_event values (?, ?)', [vod_id, event_id])

    # Link(s)
    primary_twitch = vod_json['links']['primary_twitch']
    twitch_link = 'http://www.twitch.tv/gamesdonequick/v/' + primary_twitch['stripped_id'] + \
                  '?t=' + primary_twitch['start']
    conn.execute('insert into vod_link values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?)',
                 [twitch_link, vod_id])

    primary_youtube = vod_json['links']['primary_youtube']
    youtube_link = 'http://www.youtube.com/watch?time_continue=' + primary_youtube['start'] + \
                   '&v=' + primary_youtube['id']
    conn.execute('insert into vod_link values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?)',
                 [youtube_link, vod_id])

    # Runner(s)
    for runner_id in runner_ids:
        conn.execute('insert into vods_runners values (?, ?)', [vod_id, runner_id])

    conn.commit()

conn.close()
