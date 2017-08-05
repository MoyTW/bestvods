PRAGMA foreign_keys = ON;

delete from user;
insert into user values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'test@test.com', 'test user', 'password', 1);
insert into user values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'one@test.com', 'user one', 'password', 1);
insert into user values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'two@test.com', 'user two', 'password', 1);

-- Game
delete from game;
insert into game values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Super Mario 64', 1996, 'Mario in 3D!');
insert into game values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Super Panga World', 2015, 'A romhack, very hard.');
insert into game values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Dark Souls', 2011, 'SOOOOOUUUULS');
insert into game values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Freedom Planet', 2014, 'A Sonic Fangame');
insert into game values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Star Wars Jedi Knight II: Jedi Outcast', 2002, 'I never played this');
insert into game values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Star Wars Jedi Knight: Jedi Academy', 2003, 'TAKE A BATH');
insert into game values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Star Wars', 1991, 'It was for the NES? I thought it was a SNES game...');

-- Platform
delete from platform;
insert into platform values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'PC', 'Personal Computer (Windows)');
insert into platform values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'N64', 'Had a really strange controller!');
insert into platform values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'SNES', 'Super Nintendo Entertainment System. Super nostalgic.');

-- Category
delete from category;
insert into category values(null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
       '120 Star',
       'All 120 stars',
       (select id from game where name='Super Mario 64'));
insert into category values(null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
       'Any%',
       'Finish the game with no conditions',
       (select id from game where name='Super Mario 64'));
insert into category values(null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
       'Any%',
       'Finish the game with no conditions',
       (select id from game where name='Super Panga World'));
insert into category values(null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
       'Any% Kiln Skip',
       'I have no idea what this category is',
       (select id from game where name='Dark Souls'));
insert into category values(null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
       'Lilac Any%',
       'Any% using Lilac',
       (select id from game where name='Freedom Planet'));

-- Participant
delete from participant;
insert into participant values(null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Cheese05', 'https://www.twitch.tv/cheese05');
insert into participant values(null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'DoDeChehedron', 'https://www.twitch.tv/dodechehedron');
insert into participant values(null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'BubblesdelFuego', 'https://www.twitch.tv/bubblesdelfuego');
insert into participant values(null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Fladervy', 'https://www.twitch.tv/fladervy');
insert into participant values(null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'SuccinctAndPunchy', 'https://www.twitch.tv/succinctandpunchy');

-- Events
delete from event;
insert into event values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'ESA 2017', '2017-07-22', '2017-07-29', 'ESA 2017 had two streams!');
insert into event values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'SGDQ 2017', '2017-07-02', '2017-07-09', 'The FF7 run was surprisingly good.');
insert into event values (null, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'AGDQ 2017', '2017-01-08', '2017-01-14', 'AWFUL BLOCK YES');

-- VoDs
delete from vod;
delete from vods_runners;
delete from vods_commentators;

insert into vod values(
       null,
       CURRENT_TIMESTAMP,
       CURRENT_TIMESTAMP,
       6100,
       CURRENT_DATE,
       (select id from game where name='Super Mario 64'),
       (select id from platform where name='N64'),
       (select id from category where name='120 Star'));
insert into vods_event values(
       (select id from vod where game_id=(select id from game where name='Super Mario 64')),
       (select id from event where name='SGDQ 2017'));
insert into vods_runners values(
       (select last_insert_rowid()),
       (select id from participant where handle='Cheese05'));

insert into vod values(
       null,
       CURRENT_TIMESTAMP,
       CURRENT_TIMESTAMP,
       2003,
       CURRENT_DATE,
       (select id from game where name='Super Panga World'),
       (select id from platform where name='SNES'),
       (select id from category where name='Any%'));
insert into vods_event values(
       (select id from vod where game_id=(select id from game where name='Super Panga World')),
       (select id from event where name='ESA 2017'));
insert into vods_runners values(
       (select last_insert_rowid()),
       (select id from participant where handle='DoDeChehedron'));

insert into vod values(
       null,
       CURRENT_TIMESTAMP,
       CURRENT_TIMESTAMP,
       1745,
       CURRENT_DATE,
       (select id from game where name='Dark Souls'),
       (select id from platform where name='PC'),
       (select id from category where name='Any% Kiln Skip'));
insert into vods_event values(
       (select id from vod where game_id=(select id from game where name='Dark Souls')),
       (select id from event where name='AGDQ 2017'));
insert into vods_runners values(
       (select last_insert_rowid()),
       (select id from participant where handle='BubblesdelFuego'));

insert into vod values(
       null,
       CURRENT_TIMESTAMP,
       CURRENT_TIMESTAMP,
       2656,
       CURRENT_DATE,
       (select id from game where name='Freedom Planet'),
       (select id from platform where name='PC'),
       (select id from category where name='Lilac Any%'));
insert into vods_runners values(
       (select last_insert_rowid()),
       (select id from participant where handle='Fladervy'));
insert into vods_commentators values(
       (select id from vod where game_id=(select id from game where name='Freedom Planet')),
       (select id from participant where handle='SuccinctAndPunchy'));

-- Tags
delete from tag;
insert into tag values('funny', 'hilarious!');
insert into tag values('good commentary', 'good commentary');
insert into tag values('technical', 'really impressive execution');

-- User Recs
delete from user_rec; delete from user_recs_tags;
insert into user_rec values(null,
       '120 star is da best',
       (select id from user where email='one@test.com'),
       (select id from vod where game_id=(select id from game where name='Super Mario 64')));
insert into user_recs_tags values((select last_insert_rowid()), 'funny');
insert into user_recs_tags values((select last_insert_rowid()), 'technical');
insert into user_rec values(null,
       'S&P is fun times',
       (select id from user where email='one@test.com'),
       (select id from vod where game_id=(select id from game where name='Freedom Planet')));
insert into user_recs_tags values((select last_insert_rowid()), 'good commentary');
insert into user_rec values(null,
       'I too like 120 star',
       (select id from user where email='two@test.com'),
       (select id from vod where game_id=(select id from game where name='Super Mario 64')));
