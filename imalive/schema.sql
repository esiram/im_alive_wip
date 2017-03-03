drop table if exists table_survivors;
create table table_survivors (
  id integer primary key autoincrement,
  familyName text not null,
  personalName text not null,
  additionalname text not null,
  gender text not null,
  age integer not null,
  year integer not null,
  month integer not null,
  day integer no null,
  country text not null,
  city text not null,
  county text not null,
  village text not null,
  other text not null,
  sos text not null,
  otherSOS text not null,
  password text not null,
  signupDate timestamp,
  updateDate timestamp
);
