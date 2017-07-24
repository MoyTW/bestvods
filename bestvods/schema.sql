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
