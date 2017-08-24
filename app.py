######################################
# author of skeleton code ben lawson <balawson@bu.edu> 
# project completed by Lida Karadimou <ledakar@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login

#for image uploading
from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = ‘******’  # Change this to your secret key!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '******'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users") 
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users") 
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd 
	return user


@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out') 

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html') 

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress=True)  

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getUserFirstNameFromID(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT firstname FROM Users WHERE user_id = '{0}'".format(user_id))
	return cursor.fetchone()[0]

def getUserLastNameFromID(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT lastname FROM Users WHERE user_id = '{0}'".format(user_id))
	return cursor.fetchone()[0]


def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)): 
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

@app.route("/register", methods=['POST'])
def register_user():
	try:
		firstname = request.form.get('firstname')
		lastname = request.form.get('lastname')
		dateofbirth = request.form.get('dateofbirth')
		email=request.form.get('email')
		password=request.form.get('password')
		hometown = request.form.get('hometown')
		gender = request.form.get('gender')
	except:
		print "couldn't find all tokens" #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print cursor.execute("INSERT INTO Users (firstname, lastname, dateofbirth, email, password, hometown, gender) VALUES ('{0}', '{1}','{2}','{3}','{4}','{5}','{6}')".format(firstname, lastname, dateofbirth, email, password, hometown, gender))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=firstname, message='Account Created!')
	else:
		print "couldn't find all tokens"
		return flask.redirect(flask.url_for('register',message='ERROR!:User already exist'))


#adding a friendship
@app.route("/add", methods= ['GET', 'POST'])
@flask_login.login_required
def add_friend():
	if request.method == 'POST':
		user_id1 = getUserIdFromEmail(flask_login.current_user.id)
		email = request.form.get('email')
		test =  isEmailUnique(email)
		if not test:
			user_id2 = getUserIdFromEmail(email)
			print email
			cursor = conn.cursor()
			try:
				cursor.execute("INSERT INTO Friends (user_id1, user_id2) VALUES ('{0}', '{1}')".format(user_id1,user_id2))
				conn.commit()
				cursor.execute("INSERT INTO Friends (user_id1, user_id2) VALUES ('{0}', '{1}')".format(user_id2,user_id1))
				conn.commit()
				return render_template('hello.html', name=flask_login.current_user.id, message='Friend Added!')
			except:
				print("already friends")
				return render_template('add.html', message='already friends!!!!!!') #if already friends
		else: 
			return render_template('hello.html',name=flask_login.current_user.id, message='Sorry, user does not exist')
	else:
		return render_template('add.html')


#displaying friends
@app.route("/friends",methods= ['GET','POST'])
@flask_login.login_required
def view_friends():
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	if request.method=='GET':
		print getUsersFriends(user_id)
		return render_template('friends.html', name=flask_login.current_user.id, friends=getUsersFriends(user_id))


#getFriends to be used in page for displaying friends
def getUsersFriends(user_id):
	cursor = conn.cursor()
	try:
		cursor.execute("SELECT DISTINCT firstname, lastname FROM Users U, (SELECT user_id2 FROM Friends WHERE user_id1 = '{0}') F WHERE U.user_id=F.user_id2".format(user_id))
		return cursor.fetchall()
	except:
		cursor.execute("SELECT DISTINCT firstname, lastname FROM Users U, (SELECT user_id1 FROM Friends WHERE user_id2 = '{0}') F WHERE U.user_id=F.user_id1".format(user_id))
		return cursor.fetchall()
	#except render_template('friends.html',message = 'you have no friends...')


@app.route('/searchforfriends',methods= ['GET','POST'])
def searchForFriends():
	if request.method == 'POST':
		firstname = request.form.get('firstname')
		return render_template('searchforfriends.html',  people=getSearchResults(firstname), friendsearchmessage='check if you want to add any of these emails')
	else:
		return render_template('searchforfriends.html')

@app.route('/searchforuserbyID',methods= ['GET','POST'])
def searchForUserbyId():
	if request.method == 'POST':
		user_id = request.form.get('user_id')
		return render_template('searchforuserbyID.html',  people=getSearchResultsbyID(user_id), friendsearchmessage='this is the email of the user id you searched for')
	else:
		return render_template('searchforuserbyID.html')

def getSearchResults(firstname):
	cursor = conn.cursor()
	cursor.execute("SELECT email FROM Users WHERE firstname = '{0}'".format(firstname))
	return cursor.fetchall()

def getSearchResultsbyID(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT email FROM Users WHERE user_id = '{0}'".format(user_id))
	return cursor.fetchall()

#view the top contributors page
@app.route("/topten",methods= ['GET','POST'])
def view_contributions():
	if request.method=='GET':
		print getContributions()
		return render_template('topten.html', contributions=getContributions())

#getContributions to be used for viewing the top contributors
def getContributions():
	cursor = conn.cursor()
	cursor.execute("SELECT lastname, COUNT(*) FROM contributions GROUP BY lastname ORDER BY COUNT(*) DESC LIMIT 10;")
	conn.commit()
	return cursor.fetchall()


def getUsersPhotos(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id FROM Pictures WHERE user_id = '{0}'".format(user_id))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]


@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


#upload a new photo
@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_photo():
	if request.method == 'POST':
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		album_id = request.form.get('album_id')
		print album_id
		caption = request.form.get('caption')
		print caption
		photo_data = base64.standard_b64encode(imgfile.read())
		cursor = conn.cursor()
		cursor.execute("SELECT user_id FROM Albums WHERE album_id='{0}'".format(album_id)) #to check later if this belongs to logged in user
		conn.commit()
		if cursor.fetchone()==None:
			return render_template('upload.html', message='album does not exist')
		else:
			cursor = conn.cursor()
			cursor.execute("SELECT user_id FROM Albums WHERE album_id='{0}'".format(album_id))
			album_check= cursor.fetchone()[0]
			if ((album_check == user_id)):
				firstname= getUserFirstNameFromID(user_id)
				lastname= getUserLastNameFromID(user_id)
				cursor.execute("INSERT INTO Pictures (imgdata, user_id, album_id, caption) VALUES ('{0}', '{1}', '{2}', '{3}' )".format(photo_data,user_id, album_id, caption))
				conn.commit()
				cursor.execute("INSERT INTO Contributions (user_id, firstname, lastname) VALUES ('{0}','{1}','{2}' )".format(user_id, firstname, lastname))
				conn.commit()
				#conn.commit()
				return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(user_id) )
			else:
				return render_template('upload.html', message='this album is not yours')
		#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')



		
#end photo uploading code 



@app.route('/createalbum', methods=['GET', 'POST'])
@flask_login.login_required
def createAlbum():
	if request.method == 'POST':
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		name = request.form.get('name')
		print name
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Albums (user_id, name) VALUES ('{0}','{1}')".format(user_id, name))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Album Created!')
	else:
		return render_template('createalbum.html')

@app.route('/deletealbum', methods=['GET', 'POST'])
@flask_login.login_required
def deleteAlbum():
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		albs = getAlbums(user_id)
		album_id = request.form.get('album_id')
		cursor.execute("SELECT * FROM (Albums NATURAL JOIN Users) WHERE album_id='{0}'".format(album_id))
		conn.commit()
		if cursor.fetchone()==None:
			return render_template('deletealbum.html', message='album does not exist',albs=getAlbumid(user_id))
		else:
			cursor.execute("SELECT user_id FROM (Albums NATURAL JOIN Users) WHERE album_id='{0}'".format(album_id))
			album_check= cursor.fetchone()[0] #to check that the user has an album with that id
			if (album_check == user_id):
				#cursor.execute("SELECT user_id ")
				cursor.execute("DELETE FROM Albums WHERE album_id='{0}'". format(album_id))
				conn.commit()
				return render_template('hello.html', name=flask_login.current_user.id, message='Album Deleted!',albs=getAlbumid(user_id))
			else:
				return render_template('deletealbum.html', message="This album is not yours!!!", albs=getAlbumid(user_id))
	else:
		return render_template('deletealbum.html')


@app.route('/deletephoto', methods=['GET', 'POST'])
@flask_login.login_required            
def deletePhoto():
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		#phts = getPhotos(photo_id)
		phts_id = request.form.get('picture_id')
		cursor.execute("SELECT * FROM (Pictures NATURAL JOIN Users) WHERE picture_id='{0}'".format(phts_id))
		conn.commit()
		if cursor.fetchone()==None:
			return render_template('deletephoto.html', message='photo does not exist',phts=getPhotoid(user_id))
		else:
			cursor.execute("SELECT user_id FROM (Pictures NATURAL JOIN Users) WHERE picture_id='{0}'".format(phts_id))
			conn.commit()
			photo_check= cursor.fetchone()[0] #to check that the user has a photo with that id
			if (photo_check == user_id):
				cursor.execute("DELETE FROM Pictures WHERE picture_id='{0}'". format(phts_id))
				conn.commit()
				return render_template('hello.html', name=flask_login.current_user.id, message='Photo Deleted!',phts=getPhotoid(user_id))
			else:
				return render_template('deletephoto.html', message="Something went wrong... Try again by choosing one of YOUR photos:", phts=getPhotoid(user_id))
	else:
		return render_template('deletephoto.html')

		
def getAlbums(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT name, album_id FROM Albums WHERE user_id = '{0}'".format(user_id))
	conn.commit()
	return cursor.fetchall()      #getting all the album names and album ids of a specific user

def getAlbumid(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id FROM Albums WHERE user_id = '{0}'".format(user_id))
	conn.commit()
	return cursor.fetchall()  #getting all the album ids of a specific user


#helper function to get the photo ids of all the photos a specific user has uploaded
def getPhotoid(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id FROM Pictures WHERE user_id = '{0}'".format(user_id))
	conn.commit()
	return cursor.fetchall()


#view your own photos 
@app.route('/yourphotos', methods=['GET','POST'])
@flask_login.login_required
def view_photos():
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('yourphotos.html', name=flask_login.current_user.id, message='Here are your photos', photos=getUsersPhotos(user_id))

"""
@app.route('/tag',methods=['GET,POST'])
@flask_login.login_required
def add_tag():
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	if (request.method == 'POST'):
		return render_template('tag.html', name=flask_login.current_user.id)
	else:
		return render_template('hello.html')
"""


def getAllPhotos():
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata,picture_id, name, album_id FROM (Pictures NATURAL JOIN Albums) ORDER BY album_id")
	conn.commit()
	return cursor.fetchall()

@app.route('/allphotos',methods=['GET','POST'])
def view_all_photos():
	return render_template('allphotos.html',message='These are all the photos in the database with their ids and their corresponding album names and album ids', photos=getAllPhotos())

"""
@app.route('/allphotos',methods=['GET','POST'])
#@app.route('/search')
#def new_page_function():
#    return new_page_html
"""

@app.route("/comment",methods=['GET','POST'])
@flask_login.login_required
def commentOn():
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		phts_id = request.form.get('phts_id')
		print(phts_id)
		text = request.form.get('text')
		cursor.execute("SELECT * FROM Pictures WHERE picture_id='{0}'".format(phts_id))
		conn.commit()
		if (cursor.fetchone()==None):
			return render_template('comment.html', message='photo does not exist')
		else:
			cursor.execute("SELECT user_id FROM (Pictures NATURAL JOIN Users) WHERE picture_id='{0}'".format(phts_id))
			conn.commit()
			photo_check= cursor.fetchone()[0] #to check that the user has a photo with that id
			if (photo_check == user_id):
				return render_template('comment.html', message='Error: you cannot comment on your own photo...')
			else:
				firstname= getUserFirstNameFromID(user_id)
				lastname= getUserLastNameFromID(user_id)
				cursor.execute("INSERT INTO Contributions (user_id, firstname, lastname) VALUES ('{0}','{1}','{2}' )".format(user_id, firstname, lastname))
				conn.commit() 
				cursor.execute("INSERT INTO Comments (text, user_id, picture_id) VALUES ('{0}','{1}','{2}')".format(text, user_id, phts_id))
				conn.commit()
				return render_template('comment.html',message='comment added') #vasika kane redirect stin selida tis pic me ta comments
	else:
		return render_template('comment.html')
	

@app.route("/viewcomments", methods=['GET','POST'])
def viewComments():
	picture_id = request.form.get('picture_id')
	if request.method=='POST':
		print(picture_id)
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM Pictures WHERE picture_id='{0}'".format(picture_id))
		if (cursor.fetchone()==None):
			return render_template('viewcomments.html', message='photo does not exist')
		else:
			cursor = conn.cursor()
			cursor.execute("SELECT text  FROM (Pictures INNER JOIN Comments ON Pictures.picture_id = Comments.picture_id) WHERE Comments.picture_id = '{0}'".format(picture_id))
			conn.commit()
			if (cursor.fetchone()== None):
				return render_template('viewcomments.html',message='no comments for this photo')
			else:
				return render_template('viewcomments.html',phcommts=getPhotoComments(picture_id))
	else:
		return render_template('viewcomments.html')

def getPhotoComments(picture_id):
	cursor = conn.cursor()
	cursor.execute("SELECT text,Comments.user_id  FROM (Pictures INNER JOIN Comments ON Pictures.picture_id = Comments.picture_id) WHERE Comments.picture_id = '{0}'".format(picture_id))
	return cursor.fetchall()

@app.route("/likePhoto",methods=['GET','POST'])
@flask_login.login_required
def Like():
	if request.method=='POST':
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		picture_id = request.form.get('picture_id')
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM Likes WHERE user_id= '{0}' AND picture_id = '{1}'".format(user_id,picture_id))
		if (cursor.fetchone()==None):
			cursor = conn.cursor()
			cursor.execute("SELECT * FROM Pictures WHERE picture_id='{0}'".format(picture_id))
			if (cursor.fetchone()==None):
				return render_template('likePhoto.html', message='photo does not exist')
			else:
				cursor=conn.cursor()
				cursor.execute("INSERT INTO Likes (user_id, picture_id) VALUES ('{0}','{1}')".format(user_id,picture_id))
				conn.commit()
				return render_template("likePhoto.html", message="photo liked!")
		else:
			return render_template("likePhoto.html", message="you have already liked this photo!")
	else:
		return render_template('likePhoto.html')


def LikeCount(picture_id):
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(user_id) FROM Likes WHERE picture_id='{0}'".format(picture_id))
	return cursor.fetchone()[0]

@app.route("/ViewWhoHasLiked",methods=['GET','POST'])
def ViewWhoHasLiked():
	if request.method=='POST':
		picture_id = request.form.get('picture_id')
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM Pictures WHERE picture_id='{0}'".format(picture_id))#to check first if photo exists
		if (cursor.fetchone()==None):
			return render_template("ViewWhoHasLiked.html", message="photo does not exist, check again into photo browser")
		else:
			a=getLikes(picture_id)
			b=LikeCount(picture_id)
			return render_template("ViewWhoHasLiked.html",number=b, likes=a ,message="these are the likes:")
	else:
		return render_template('ViewWhoHasLiked.html')

def getLikes(picture_id):
	cursor = conn.cursor()
	cursor.execute("SELECT firstname,lastname FROM (Likes NATURAL JOIN Users) WHERE picture_id='{0}'".format(picture_id))
	return cursor.fetchall()


@app.route("/addtag", methods=['GET','POST'])
@flask_login.login_required
def addTag():  #request.form.get('text').split
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	print(user_id)
	if request.method=='POST':
		picture_id = request.form.get('picture_id')
		text = request.form.get('text')   #request.form.get('text').split  kai meta size=length(tags) for i in length
		cursor = conn.cursor()          
		cursor.execute("SELECT * FROM Pictures WHERE user_id= '{0}' AND picture_id = '{1}'".format(user_id,picture_id))
		print(picture_id)
		if (cursor.fetchone()==None):
			return render_template("addtag.html", message="photo does not exist or is not yours")
		else:
			cursor=conn.cursor()
			cursor.execute("INSERT INTO Tags ( text, picture_id) VALUES ('{0}','{1}')".format( text , picture_id))
			conn.commit()
			return render_template("addtag.html",message="tag added, if you want add another one:")
	else:
		return render_template("addtag.html")

#getting all the tags according to picture id
def getTags(picture_id):
	cursor=conn.cursor()
	cursor.execute("SELECT text FROM Tags WHERE picture_id='{0}'".format(picture_id))
	return cursor.fetchall() 


def getPhotobyID(picture_id):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata FROM Pictures WHERE picture_id = '{0}'".format(picture_id))
	return cursor.fetchall()


@app.route("/viewaphoto", methods=['GET','POST'])
def viewaphoto():
	picture_id = request.form.get('picture_id')
	if request.method=='POST':
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM Pictures WHERE picture_id ='{0}'".format(picture_id))
		if (cursor.fetchone()==None):
			return render_template("viewaphoto.html", message="photo does not exist")
		else:
			#cursor.execute("SELECT imgdata FROM Pictures WHERE picture_id ='{0}'".format(picture_id))
			#conn.commit()
			#a=cursor.fetchone()
			return render_template("viewaphoto.html", message="here is your photo" , photo =getPhotobyID(picture_id), tmessage="and here are the tags associated with it" ,tags=getTags(picture_id))
	else:
		return render_template("viewaphoto.html")

"""

def tagLink():
	if request.method=='GET'
	return render_template('')"""

@app.route("/viewatag", methods=['GET','POST'])
def viewatag():
	text = request.form.get('text')
	return render_template("viewatag.html", photos=getPhotosbyTags(text) )

@app.route("/viewbyalbum", methods=['GET','POST']) 
def viewbyalbum():
	album = request.form.get('album')
	print(album)
	return render_template("viewbyalbum.html", albums=getPhotosbyAlbum(album)) 

def getPhotosbyAlbum(album):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata FROM (Pictures INNER JOIN Albums ON Pictures.album_id = Albums.album_id) WHERE name = '{0}'".format(album))
	return cursor.fetchall()

def getPhotosbyTags(text):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata FROM (Pictures INNER JOIN Tags ON Pictures.picture_id = Tags.picture_id) WHERE text= '{0}'".format(text))
	return cursor.fetchall()


@app.route("/mostPopularTags", methods = ['GET', 'POST'])
def mostPopularTags():
	if request.method=='GET':
		return render_template('mostPopularTags.html', popular=getmostPopularTags(), message='these are the most popular tags and the number of times they are used')


def getmostPopularTags():
	cursor = conn.cursor()
	cursor.execute("SELECT text, COUNT(picture_id) FROM TAGS GROUP BY text ORDER BY COUNT(picture_id) DESC")
	conn.commit
	return cursor.fetchall()

@app.route("/photosearch", methods = ['GET', 'POST'])
def photosearch():
	searchentry = request.form.get('searchentry')
	alltags = str(searchentry)
	tags = alltags.split(' ')
	empty=[]
	#print tags
	#print len(tags)
	#print tags[0]
	q="SELECT picture_id FROM tags WHERE text = '" + (tags[0]) + "'"
	i=1
	while i < len(tags):
		q=q+" AND picture_id IN (SELECT picture_id FROM Tags WHERE text = '" + (tags[i]) +"' )"
		i=i+1
	return render_template('photosearch.html', t=searchhelper(q))

def searchhelper(q):
	cursor = conn.cursor()
	cursor.execute(q)
	conn.commit
	return cursor.fetchall()
"""
@app.route("/mayalso", methods=['GET','POST'])
@flask_login.login_required
def mayAlso():
	getUserIdFromEmail(flask_login.current_user.id)
	return render_template('mayalso.html', res=mayAlsohelper(user_id))


def mayAlsohelper(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT text from Tags, Pictures WHERE Tags.picture_id = Pictures.picture_id and user_id='{0}' GROUP BY text HAVING COUNT(*)>0 ORDER BY COUNT(*) DESC LIMIT 5)".format(user_id))
	return cursor.fetchall()
"""

@app.route("/tag_suggestion", methods = ['GET', 'POST'])
def tag_suggestion():
	t1 = request.form.get('t1')
	t2 = request.form.get('t2')
	return render_template('tag_suggestion.html',m=tag_suggestion_helper(t1,t2))

def tag_suggestion_helper(t1,t2):
	cursor = conn.cursor()
	cursor.execute("select t.text, count(t.picture_id) from tags as t inner join pictures as p on t.picture_id = p.picture_id inner join tags as ta on p.picture_id = ta.picture_id where ta.text = '{0}' or ta.text = '{1}'  and t.text<>'{1}' and t.text<>'{0}' group by t.text order by count(t.picture_id) desc)".format(t1,t2))
	return cursor.fetchall()



#select text, count from (pictures inner join tags on Pictures.picture_id = Tags.picture_id) WHERE user_id = '{0}' group by text order by count(picture_id) desc limit 5
#select picture_id,count(picture_id) from   tag=
#default page  

"""
select text 

"""
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare')



if __name__ == "__main__":
	#this is invoked when in the shell  you run 
	#$ python app.py 
	app.run(port=5000, debug=True)
