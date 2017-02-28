drop table if exists table_survivors;
create table table_survivors (
  id integer primary key autoincrement,
  familyName text not null,
  personalName text not null,
  nickname text not null,
  sex text not null,
  age integer not null,
  originCountry text not null,
  originCity text not null,
  other text not null,
  message text not null,
  todayDate timestamp,
  username text not null,
  password text not null
);
