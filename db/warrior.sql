CREATE DATABASE warriors_db;
USE warriors_db;

CREATE TABLE warriors (
  id varchar(36) NOT NULL,
  name varchar(100) NOT NULL,
  dob varchar(10) NOT NULL,
  fight_skills varchar(5019) NOT NULL,
  PRIMARY KEY (id)
);

INSERT INTO warriors
  (id, name, dob, fight_skills)
VALUES
  ('3b323968-73d8-47a3-a84d-9db948e2bd6b', 'Neo','1962-03-11','KungFu,Judo,Taekwondo');