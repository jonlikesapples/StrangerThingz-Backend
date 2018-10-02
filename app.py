from flask import Flask, jsonify, request, session
#from flask.ext.session import Session
import os
import json
import pyrebase
import hashlib
import datetime
import random
from googlemaps import Client
#from config import *
#from . import app
#https://github.com/thisbejim/Pyrebase
'''
git add .
git commit -m "commit message"
git push heroku master
https://strangerthingz-backend.herokuapp.com

pip freeze > requirements.txt
pip install -r requirements.txt
'''

app = Flask(__name__)


herokuConfig = {
	"apiKey": os.environ["API_KEY"],
	"authDomain:": os.environ["AUTH_DOMAIN"],
	"databaseURL": os.environ["DATABASE_URL"],
	"storageBucket": os.environ["STORAGE_BUCKET"],
}

googleMapsServerKey = os.environ["GOOGLEMAPS_SERVER_KEY"];
googleMapsBrowserKey = os.environ["GOOGLEMAPS_BROWSER_KEY"];

# config = {
#   "apiKey": APIKEY,
#   "authDomain": AUTHDOMAIN,
#   "databaseURL": DATABASEURL,
#   "storageBucket": STORAGEBUCKET,
# }


# googleMapsServerKey = GOOGLEMAPSSERVERKEY
# googleMapsBrowserKey = GOOGLEMAPSBROWSERKEY

firebase = pyrebase.initialize_app(herokuConfig)
#firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth();

def getcount():
	dbresult = db.child("totalnumofusers").get()
	QUERY_RESULT = ""
	getcount = 123
	for user in dbresult.each():
		QUERY_RESULT += "key: " + str(user.key()) + " " + "val: " + str(user.val()) + "<br>"
		getcount = user.val()
	return str(getcount);

def inccount():
	dbresult = db.child("totalnumofusers").get()
	QUERY_RESULT = ""
	newcount = 123
	for user in dbresult.each():
		QUERY_RESULT += "key: " + str(user.key()) + " " + "val: " + str(user.val()) + "<br>"
		newcount = user.val() + 1;
		break;

	addcount = {"count": newcount }
	dbresult = db.child("totalnumofusers").update(addcount);
def resetcount():
	dbresult = db.child("totalnumofusers").get()
	resettedcount = {"count": 1}
	db.child("totalnumofusers").update(resettedcount);

def sha256encrypt(hash_string):
    encryptedPassword = hashlib.sha256(hash_string.encode()).hexdigest()
    return encryptedPassword

#get from firebase server.
@app.route("/")
def nothing():
	return """Welcome to the Stranger Thingz backend, powered by Flask. <br> \
	Created for CMPE195A-Senior Project at SJSU for Fall 2018 - Spring 2019. <br> \
	Authors: Gwyneth Mina, Christopher Navy, Brendan Hui, and Jonathan Wong. <br> <br> \
	possible endpoints: <br>\
	/allusers <br> \
	/authcreateuser?email=EMAIL@DOMAIN.COM&password=PASSWORD <br>\
	/authlogin?email=EMAIL@DOMAIN.COM&password=PASSWORD <br> \
	/authresetpassword?email=EMAIL@DOMAIN.COM <br> \
	/geodirections?start=START&end=END (params: literal location: "San Francisco, California" or coordinates: '37.4215420,-122.0840110') <br> \
	last commit: 7/12/2018""";

@app.route("/geodirections")
def geolocation():
	start = str(request.args.get('start'));
	end = str(request.args.get('end'));
	#start = "37.3324980,-122.0289780";
	#end = "37.4215420,-122.0840110";
	print(start);
	print(end);
	gmaps = Client(key=googleMapsServerKey);
	return json.dumps(gmaps.distance_matrix(
						start,
						end,
						'driving',
						'imperial'));

@app.route("/jsontest")
def jsontest():
	returnme = {
	"username": "hi",
	"password": "password"
	}
	return jsonify(returnme);

#works properly: password needs to be at least 8 characters long
#error handling works in front-end
@app.route("/authcreateuser")
def specialpost():
	email = str(request.args.get('email')); #gets email parameter from link ?email=EMAIL&
	print(request.args.get('email'));
	#password = sha256encrypt(str(request.args.get('password')));
	#password encryption in front end?
	password = str(request.args.get('password'));
	user = auth.create_user_with_email_and_password(email, password);

	now = datetime.datetime.now()
	data = {
	"dateCreated": str(now),
	"importantinfo": "this is the entry for: " + email
		}
	results = db.child("users").child(user['localId']).set(data)
	return "posted <br> \
	" + json.dumps(auth.get_account_info(user['idToken']));

#foo@bar.com
#foobar
@app.route("/authlogin")
def speciallogin():
	email = str(request.args.get('email'));
	password = str(request.args.get('password'));
	user = auth.sign_in_with_email_and_password(email, password);
	return str(user['localId']);
	# localid = str(user['localId']);
	# info = db.child("users").child(localid).get().val();
	# return json.dumps(info);

@app.route("/authresetpassword")
def resetpassword():
	email = str(request.args.get('email'));
	auth.send_password_reset_email(email);
	return "sent a password reset email to: " + email;

@app.route("/allusers", methods=['GET'])
def get():
	# queryresult = db.child("users").get().val() #type orderedDict
	# data = json.loads(json.dumps(queryresult)) #type (regular) dict
	# stringdata = json.dumps(data) #type string, no real use for this
	QUERY_RESULT = ""
	dbresult = db.child("users").get() #type orderedDict
	for user in dbresult.each():
		QUERY_RESULT += "key: " + str(user.key()) + " " + "val: " + str(user.val()) + "<br>"
	return QUERY_RESULT;

@app.route('/getcurrentcount') #gets total count
def count():
	return "current count at  .../totalnumofusers/count is: " + getcount();

#Format: /post?username=(username)&password=(password)
#if post has no params, will just post username: "None" | password: "None"
@app.route('/post')
def redirect():
	return "don't use this endpoint."
	usernameValue = str(request.args.get('username'));
	passwordValue = sha256encrypt(str(request.args.get('password')));
	postedvalue = {"username": usernameValue,
				   "password": passwordValue,
				   "info": "this is info of " + usernameValue}
	#ALWAYS USE .UPDATE to post, will create a new key too
	#.update has to take in a JSON object.
	endpoint = "testaccount" + getcount();
	db.child("users").child(endpoint).update(postedvalue);
	inccount();
	return json.dumps(postedvalue);
	#return json.loads(json.dumps(postedvalue));

@app.route("/deleteallusers")
def delete():
	return "dont use this endpoint."
	resetcount();
	db.child("users").remove()
	return "deleted all users and reset count to 1"


##################################################################################################################################
#######################################[DON'T TOUCH] Serverside stuff to connect to Heroku #######################################
##################################################################################################################################
if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.config['SESSION_TYPE'] = 'filesystem'
	#sess.init_app(app)
	app.debug = True
	from os import environ;
	app.run(debug=True, host='0.0.0.0', port=int(environ.get("PORT", 5000)));
