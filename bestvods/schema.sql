/* Users and Roles */

drop table if exists user;
create table user (
       id integer primary key autoincrement,
       email text not null,
       password text not null,
       active boolean not null
);

drop table if exists role;
create table role (
       id integer primary key autoincrement,
       name text not null,
       description text not null
);

drop table if exists roles_users;
create table roles_users (
       user_id integer not null,
       role_id integer not null,

       foreign key (user_id) references user(id),
       foreign key (role_id) references role(id)
);

/* VoDs */

drop table if exists category;
create table category (
       name text primary key,
       description text not null
);

drop table if exists game;
create table game (
       name text not null,
       release_year integer not null,

       description text not null,

       primary key (name, release_year)
);

drop table if exists platform;
create table platform (
       name text not null primary key,
       description text not null
);

drop table if exists vod;
create table vod (
       id integer primary key autoincrement,
       run_time_seconds integer not null,

       game_name text not null,
       game_release_year integer not null,
       platform_id integer not null,
       category_id integer not null,

       foreign key (game_name, game_release_year) references game(name, release_year),
       foreign key (platform_id) references platform(id),
       foreign key (category_id) references category(id)
);

/* VoD participants */

drop table if exists participant;
create table participant (
       id integer primary key autoincrement,
       handle text not null,
       stream_url text not null
);

drop table if exists vods_runners;
create table vods_runners (
       vod_id integer not null,
       participant_id integer not null,

       foreign key (vod_id) references vod(id),
       foreign key (participant_id) references participant(id)
);

drop table if exists vods_commentators;
create table vods_commentators (
       vod_id integer not null,
       participant_id integer not null,

       foreign key (vod_id) references vod(id),
       foreign key (participant_id) references participant(id)
);

/* Recommendations & Tags */

drop table if exists tag;
create table tag (
       name text primary key,
       description text not null
);

drop table if exists user_rec;
create table user_rec (
       id integer primary key autoincrement,
       description text not null,

       user_id integer not null,
       vod_id integer not null,

       foreign key (user_id) references user(id),
       foreign key (vod_id) references vod(id)
);

drop table if exists user_recs_tags;
create table user_recs_tags (
       user_rec_id integer not null,
       tag_id integer not null,

       foreign key (user_rec_id) references user_rec(id),
       foreign key (tag_id) references tag(id)
);
