drop table if exists survivors;
create table survivors (
  id integer primary key autoincrement,
  familyName text NOT NULL,
  personalName text NOT NULL,
  additionalName text,
  gender text NULL,
  age integer NULL,
  year integer NULL,
  month integer NULL,
  day integer NULL,
  country text NULL,
  state text NULL,
  city text NULL,
  county text NULL,
  village text NULL,
  other text NULL,
  sos text NULL,
  otherSOS text NULL,
  password text NOT NULL,
  signupDate timestamp NOT NULL,
  updateDate timestamp NULL
);
