drop table if exists urls;
drop table if exists users;

create table users (
	id integer primary key autoincrement,
	username text not null,
	password text not null
);

create table urls (
	id integer primary key autoincrement,
	short text not null,
	long text not null,
	uid integer,
	custom boolean,
	FOREIGN KEY (uid) REFERENCES users(id)
);
