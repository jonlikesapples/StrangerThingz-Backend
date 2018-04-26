from flask import Flask, jsonify, request
import os
import json
import pyrebase
import hashlib
import datetime
#https://github.com/thisbejim/Pyrebase
'''
git add .
git commit -m "commit message"
git push heroku master
https://strangerthingz-backend.herokuapp.com
'''
app = Flask(__name__)


#####################################[DON'T TOUCH] FIREBASE CONFIG #############################################
config = {
  "apiKey": "AIzaSyAb0csAFZDQoYIJrflFTuYAwx7rS1t3oYg",
  "authDomain": "stranger-things-ce12a.firebaseapp.com",
  "databaseURL": "https://stranger-things-ce12a.firebaseio.com/",
  "storageBucket": "stranger-things-ce12a.appspot.com",
}
################################################################################################################

'''
TODO: 
ENCRYPT PASSWORD (FRONT END)
increment count everytime you add an account
- won't push if username already exists
delete one individual account, based on username
'''

firebase = pyrebase.initialize_app(config)

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
	return "Welcome to the Stranger Thingz backend, powered by Flask. <br> \
	Created for CMPE195A-Senior Project at SJSU for Fall 2018 - Spring 2019. <br> \
	Authors: Gwyneth Mina, Christopher Navy, Brendan Hui, and Jonathan Wong. <br> <br> \
	possible endpoints: <br>\
	/allusers <br> \
	/authpost?email=EMAIL@DOMAIN.com&password=PASSWORD <br>\
	/authlogin?email=EMAIL@DOMAIN.COM&password=PASSWORD <br> \
	last commit: 4/25/2018"

@app.route("/test")
def test():
	now = datetime.datetime.now()
	print str(now)
	return "this endpoint exists only for testing"

#DOESN'T WORK PROPERLY
@app.route("/authpost")
def specialpost():
	email = str(request.args.get('email'));
	#password = sha256encrypt(str(request.args.get('password')));
	password = str(request.args.get('password'));
	user = auth.create_user_with_email_and_password(email, password);

	now = datetime.datetime.now()
	print str(now)

	data = {
	"dateCreated": str(now),
	"importantinfo": "this is the entry for: " + email
		}

	results = db.child("users").child(user['localId']).set(data)
	return "posted <br> \
	" + json.dumps(auth.get_account_info(user['idToken']));

#ALSO WORK PROPERLY
@app.route("/authlogin")
def speciallogin():
	email = str(request.args.get('email'));
	#password = sha256encrypt(str(request.args.get('password')));
	password = str(request.args.get('password'));	
	user = auth.sign_in_with_email_and_password(email, password);
	localid = str(user['localId']);
	info = db.child("users").child(localid).get().val();
	return json.dumps(info);

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
    from os import environ;
    app.run(debug=True, host='0.0.0.0', port=int(environ.get("PORT", 5000)));

    