-- Game
delete from game;
insert into game values ('Super Mario 64', 1996, 'Mario in 3D!');
insert into game values ('Super Panga World', 2015, 'A romhack, very hard.');
insert into game values ('Dark Souls', 2011, 'SOOOOOUUUULS');
insert into game values ('Freedom Planet', 2014, 'A Sonic Fangame');


-- Platform
delete from platform;
insert into platform values ('PC', 'Personal Computer (Windows)');
insert into platform values ('N64', 'Had a really strange controller!');
insert into platform values ('SNES', 'Super Nintendo Entertainment System. Super nostalgic.');

-- Category
delete from category;
insert into category values('120 Star', 'All 120 stars');
insert into category values('Any%', 'Finish the game with no conditions');
insert into category values('Any% Kiln Skip', 'I have no idea what this category is');
insert into category values('Lilac Any%', 'Any% using Lilac');

-- VoD
delete from vod;
insert into vod values(null, 6100, 'Super Mario 64', 1996, 'N64', '120 Star');
insert into vod values(null, 2003, 'Super Panga World', 2015, 'SNES', 'Any%');
insert into vod values(null, 1745, 'Dark Souls', 2011, 'PC', 'Any% Kiln Skip');
insert into vod values(null, 2656, 'Freedom Planet', 2014, 'PC', 'Lilac Any%');

-- Participant
delete from participant;
insert into participant values(null, 'Cheese05', 'https://www.twitch.tv/cheese05');
insert into participant values(null, 'DoDeChehedron', 'https://www.twitch.tv/dodechehedron');
insert into participant values(null, 'BubblesdelFuego', 'https://www.twitch.tv/bubblesdelfuego');
insert into participant values(null, 'Fladervy', 'https://www.twitch.tv/fladervy');
insert into participant values(null, 'SuccinctAndPunchy', 'https://www.twitch.tv/succinctandpunchy');

-- VoDs->Runners
delete from vods_runners;
insert into vods_runners values(
       (select id from vod where game_name='Super Mario 64'),
       (select id from participant where handle='Cheese05'));
insert into vods_runners values(
       (select id from vod where game_name='Super Panga World'),
       (select id from participant where handle='DoDeChehedron'));
insert into vods_runners values(
       (select id from vod where game_name='Dark Souls'),
       (select id from participant where handle='BubblesdelFuego'));
insert into vods_runners values(
       (select id from vod where game_name='Freedom Planet'),
       (select id from participant where handle='Fladervy'));

-- VoDs->Commentators
delete from vods_commentators;
insert into vods_commentators values(
       (select id from vod where game_name='Freedom Planet'),
       (select id from participant where handle='SuccinctAndPunchy'));
