PRAGMA foreign_keys = ON;

/* Users and Roles */

drop table if exists user;
create table user (
       id integer primary key autoincrement,
       timestamp_created text not null,
       timestamp_modified text not null,
       email text not null,
       username text not null,
       password text not null,
       active boolean not null
);

drop table if exists role;
create table role (
       id integer primary key autoincrement,
       timestamp_created text not null,
       timestamp_modified text not null,

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

drop table if exists game;
create table game (
       id integer primary key autoincrement,
       timestamp_created text not null,
       timestamp_modified text not null,

       name text not null,
       release_year integer not null,

       description text not null,

       unique (name, release_year)
);

drop table if exists category;
create table category (
       id integer primary key autoincrement,
       timestamp_created text not null,
       timestamp_modified text not null,

       name text not null,
       description text not null,

       game_id integer not null,

       unique (name, game_id),
       foreign key(game_id) references game(id)
);

drop table if exists platform;
create table platform (
       id integer primary key autoincrement,
       timestamp_created text not null,
       timestamp_modified text not null,

       name text not null unique,
       description text not null
);

drop table if exists event;
create table event (
       id integer primary key autoincrement,
       timestamp_created text not null,
       timestamp_modified text not null,

       name text not null unique,
       -- sqlite has no date storage type - unfortunate...
       date_start text not null, -- YYYY-MM-DD
       date_end text not null, -- YYYY-MM-DD
       description text not null
);

drop table if exists vods_event;
create table vods_event (
       vod_id integer not null unique,
       event_id integer not null,

       primary key (vod_id, event_id)
       foreign key (vod_id) references vod(id),
       foreign key (event_id) references event(id)
);

drop table if exists vod;
create table vod (
       id integer primary key autoincrement,
       timestamp_created text not null,
       timestamp_modified text not null,

       run_time_seconds integer not null,
       date_completed text not null, -- YY-MM-DD

       game_id integer not null,
       platform_id integer not null,
       category_id integer not null,

       foreign key (game_id) references game(id),
       foreign key (platform_id) references platform(id),
       foreign key (category_id) references category(id)
);

drop table if exists vod_links;
create table vod_links (
       uri text primary key,
       vod_id integer not null,
       foreign key(vod_id) references vod(id)
);

/* VoD participants */

drop table if exists participant;
create table participant (
       id integer primary key autoincrement,
       timestamp_created text not null,
       timestamp_modified text not null,

       handle text not null unique,
       stream_url text not null
);

drop table if exists vods_runners;
create table vods_runners (
       vod_id integer not null,
       participant_id integer not null,

       primary key (vod_id, participant_id)
       foreign key (vod_id) references vod(id),
       foreign key (participant_id) references participant(id)
);

drop table if exists vods_commentators;
create table vods_commentators (
       vod_id integer not null,
       participant_id integer not null,

       primary key (vod_id, participant_id),
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
       tag_name text not null,

       foreign key (user_rec_id) references user_rec(id),
       foreign key (tag_name) references tag(name)
);
