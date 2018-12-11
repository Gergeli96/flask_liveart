drop table if exists users;
create table users (
  id serial PRIMARY KEY,
  name VARCHAR (30),
  email VARCHAR (100),
  username VARCHAR (100),
  password VARCHAR (100),
);

drop table if exists images;
create table images (
  id serial PRIMARY KEY,
  name VARCHAR (210),
  category VARCHAR (45),
);

drop table if exists chategories;
create table chategories (
  id serial PRIMARY KEY,
  category VARCHAR (45)
);
