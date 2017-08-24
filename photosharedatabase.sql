CREATE DATABASE photosharedatabase;
USE photosharedatabase;
DROP TABLE Pictures;
DROP TABLE Users;

CREATE TABLE User
(
uid int4  AUTO_INCREMENT NOT NULL,
fname VARCHAR(11) NOT NULL,
lname VARCHAR(11) NOT NULL, 
email VARCHAR(15) UNIQUE NOT NULL, 
dob DATE NOT NULL, 
hometown VARCHAR(11),
gender BOOLEAN, 
password VARCHAR(20) NOT NULL,    
PRIMARY KEY(uid)
);

CREATE TABLE Album
(
albumid int4  AUTO_INCREMENT NOT NULL,
name VARCHAR(20) NOT NULL, 
uid INT NOT NULL,
PRIMARY KEY (albumid),
FOREIGN KEY uid REFERENCES user(uid),
ON DELETE CASCADE
);

CREATE TABLE Photo
(
photoid int4  AUTO_INCREMENT NOT NULL,
caption VARCHAR(150),
data blob,
albumid INT NOT NULL,
PRIMARY KEY (photoid),
FOREIGN KEY albumid REFERENCES album(albumid)
ON DELETE CASCADE
);

CREATE TABLE Tag
(
text VARCHAR(30)
);

CREATE TABLE Comment
(
commentid int4  AUTO_INCREMENT NOT NULL,
text VARCHAR(150) NOT NULL,
uid INT NOT NULL,
photoid INT NOT NULL,
PRIMARY KEY (commentid),
FOREIGN KEY uid REFERENCES user(uid)
ON DELETE CASCADE,
FOREIGN KEY photoid REFERENCES photo(photoid)
ON DELETE CASCADE, 
CONSTRAINT uid.user != uid.photo
);

CREATE TABLE Wrote
(
date DATE NOT NULL, 
uid INT NOT NULL,
commentid INT NOT NULL, 
PRIMARY KEY (uid, commentid)
);

CREATE TABLE Created
(
dateofcreation DATE NOT NULL, 
uid INT NOT NULL, 	
albumid INT NOT NULL,
PRIMARY KEY(albumid, uid)
);

CREATE TABLE Commenton
(
commentid INT NOT NULL,
photoid INT NOT NULL,
PRIMARY KEY (photoid,commentid)
);

CREATE TABLE Has
(
text VARCHAR(255),
photoid INT,
PRIMARY KEY(text,photoid)
);


CREATE TABLE Belongsto
(
albumid VARCHAR(20) NOT NULL,
photoid VARCHAR(11) NOT NULL,
PRIMARY KEY(photoid, albumid)
);

CREATE TABLE Friends
(
uid1 INT NOT NULL, 
uid2 INT NOT NULL,
PRIMARY KEY(uid1, uid2),
FOREIGN KEY uid1 REFERENCES user(uid1),
FOREIGN KEY uid2 REFERENCES user(uid2)
);

CREATE TABLE Likes
(
uid INT NOT NULL,
photoid INT NOT NULL,
PRIMARY KEY(photoid, uid)
);

INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');




