drop table if exists survivors;
create table survivors (
  id integer primary key autoincrement,
  familyName text,
  personalName text,
  additionalName text,
  gender text,
  age integer,
  year integer,
  month integer,
  day integer,
  country text,
  city text,
  county text,
  village text,
  other text,
  sos text,
  otherSOS text,
  password text,
  signupDate timestamp,
  updateDate timestamp
);
