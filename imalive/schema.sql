drop table if exists survivors;
create table survivors (
  id integer primary key autoincrement,
  familyName text NOT NULL,
  personalName text NOT NULL,
  additionalName text,
  gender text NULL,
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
  password text NOT NULL,
  signupDate timestamp,
  updateDate timestamp
);
