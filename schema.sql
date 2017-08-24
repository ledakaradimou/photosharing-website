CREATE DATABASE photoshare;
USE photoshare;
#DROP TABLE Users CASCADE;
#DROP TABLE Albums CASCADE;
#DROP TABLE Pictures CASCADE;
#DROP TABLE Tags CASCADE;
#DROP TABLE Comments CASCADE;
#DROP TABLE Friends CASCADE;
#DROP TABLE Likes CASCADE;
#DROP TABLE Wrote CASCADE;
#DROP TABLE Created CASCADE;
#DROP TABLE Commenton CASCADE;
#DROP TABLE Belongsto CASCADE;
#DROP TABLE Has CASCADE;
#DROP TABLE Contributions CASCADE;

CREATE TABLE Users 
( firstname VARCHAR(11) NOT NULL,
  lastname VARCHAR(11) NOT NULL,
  dateofbirth DATE NOT NULL,
  email varchar(255) UNIQUE NOT NULL,
  password varchar(255) NOT NULL,
  hometown VARCHAR(11),
  gender BOOLEAN, 
  user_id int4  AUTO_INCREMENT,
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

INSERT INTO Users (firstname, lastname, dateofbirth, email, password, hometown, gender) VALUES ('Anonymous', 'Anonymous', '1001-01-01' ,'anonymous','anonymous','anonymous','1');
#for the anonymous/unregistered user

CREATE TABLE Albums
(
album_id int4 AUTO_INCREMENT,
name VARCHAR(20) NOT NULL, 
user_id INT NOT NULL REFERENCES Users(user_id),
CONSTRAINT album_pk PRIMARY KEY (album_id),
CONSTRAINT album_fk FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

#INSERT INTO Albums (album_id, name, user_id) VALUES ('0000','test','1');



CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  user_id int4,
  imgdata LONGBLOB,
  album_id int4,
  caption VARCHAR(255),
  #INDEX upid_idx (user_id),
  #tag_text VARCHAR(30) REFERENCES Tags(tag_text),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id),
  CONSTRAINT pictures_fk2 FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE,
  CONSTRAINT pictures_fk1 FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
  
);

CREATE TABLE Tags
( tag_id int4 AUTO_INCREMENT,
  picture_id int4 NOT NULL,
  text VARCHAR(30) NOT NULL,
  CONSTRAINT tag_pk PRIMARY KEY (tag_id),
  CONSTRAINT tag_fk FOREIGN KEY (picture_id) REFERENCES Pictures (picture_id) ON DELETE CASCADE
);
CREATE TABLE Comments
(
comment_id int4  AUTO_INCREMENT,
text VARCHAR(150) NOT NULL,
user_id INT NOT NULL,
picture_id INT NOT NULL,
CONSTRAINT comments_pk PRIMARY KEY (comment_id),
CONSTRAINT comments_fk1 FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE,
CONSTRAINT comments_fk2 FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Friends
(
  user_id1 INT4 NOT NULL, 
  user_id2 INT4 NOT NULL,
  CONSTRAINT friends_pk PRIMARY KEY (user_id1, user_id2),
  CONSTRAINT friends_fk1 FOREIGN KEY (user_id1) REFERENCES Users(user_id) ON DELETE CASCADE,
  CONSTRAINT friends_fk2 FOREIGN KEY (user_id2) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Likes
(
  user_id INT4 NOT NULL,
  picture_id INT4 NOT NULL,
  CONSTRAINT likes_pk PRIMARY KEY (user_id, picture_id)
);



CREATE TABLE Contributions
(
  contribution_id int4 AUTO_INCREMENT,
  user_id int4 NOT NULL,
  firstname VARCHAR(11) NOT NULL, 
  lastname VARCHAR(11) NOT NULL, 
  CONSTRAINT contr_pk PRIMARY KEY (contribution_id),
  CONSTRAINT contr_fk FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE)
  
  
#INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
#INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
