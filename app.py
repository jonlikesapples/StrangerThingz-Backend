from flask import Flask, jsonify, request, session
import utils.responses as responses
from utils.responses import *
from utils.hashing import *
from utils.config import *
#from flask.ext.session import Session
import os
import json
from boto3.session import Session
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
import hashlib
import datetime
import random
# from googlemaps import Client


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

# config = {
# 	'apiKey': os.environ["API_KEY"],
# 	'authDomain': os.environ["AUTH_DOMAIN"],
# 	'databaseURL' : os.environ["DATABASE_URL"],
# 	'storageBucket' :  os.environ["STORAGE_BUCKET"],
# }

session = Session(
    aws_access_key_id=os.environ['AWS_ACCESS_KEY'],
    aws_secret_access_key=os.environ['AWS_SECRET_KEY'],
    region_name=os.environ['AWS_REGION_NAME']
)
googleMapsServerKey = os.environ['GOOGLEMAPS_SERVER_KEY']
googleMapsBrowserKey = os.environ['GOOGLEMAPS_BROWSER_KEY']

# config = {
#   "apiKey": APIKEY,
#   "authDomain": AUTHDOMAIN,
#   "databaseURL": DATABASEURL,
#   "storageBucket": STORAGEBUCKET,
# }
# googleMapsServerKey = GOOGLEMAPSSERVERKEY
# googleMapsBrowserKey = GOOGLEMAPSBROWSERKEY

# firebase = pyrebase.initialize_app(config)
# db = firebase.database()
# auth = firebase.auth()

dynamodb = session.resource('dynamodb')
table = dynamodb.Table('195UserTable')


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
	for user in dbresult.each(): #
		QUERY_RESULT += "key: " + str(user.key()) + " " + "val: " + str(user.val()) + "<br>"
		newcount = user.val() + 1;
		break;

	addcount = {"count": newcount }
	dbresult = db.child("totalnumofusers").update(addcount);

def resetcount():
	dbresult = db.child("totalnumofusers").get()
	resettedcount = {"count": 1}
	db.child("totalnumofusers").update(resettedcount);

# def sha256encrypt(hash_string):
#     encryptedPassword = hashlib.sha256(hash_string.encode()).hexdigest()
#     return encryptedPassword

#get from firebase server.
@app.route("/")
def nothing():
	return """Welcome to the Stranger Thingz backend, powered by Flask. <br> \
	Created for CMPE195A-Senior Project at SJSU for Fall 2018 - Spring 2019. <br> \
	Authors: Gwyneth Mina, Christopher Navy, Brendan Hui, and Jonathan Wong. <br> <br> \
	last commit: 11/28/2018""";

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

#firstName, lastName, password(hashed), user_id (hash of email+ password), email, birthday
@app.route("/createUser", methods=['POST'])
def createUser():
	loadMe = json.dumps(request.form)
	userInfo = json.loads(loadMe) #type dict
	try:
		uuid = generate_uuid(userInfo);
		response = dynamodb.Table("195UserTable").put_item(
				Item={
					'userID' : uuid,
					'firstName': userInfo["firstName"].lower(),
					'lastName': userInfo["lastName"].lower(),
					'password': sha256encrypt(userInfo["password"]),
					'email' : userInfo["email"].lower(),
					"birthday" : userInfo["birthday"].lower()
				}
			)
	except Exception as e:
		return response_with(responses.INVALID_FIELD_NAME_SENT_422, value={"value": str(e)})
	else:
		return response_with(responses.SUCCESS_200, value={"value" : uuid});


@app.route("/signinUser", methods=['POST'])
def signinUser():
	loadMe = json.dumps(request.form)
	userInfo = json.loads(loadMe);
	try:
		uuid = generate_uuid(userInfo);
		response = dynamodb.Table("195UserTable").get_item(
			Key={
					'userID' : uuid,
				}
			)
		item = response['Item'];
		# return jsonify(item);
	except Exception as e:
	 	return response_with(responses.UNAUTHORIZED_401, value={"value": str(e)})
	else:
		userUUID = json.loads(json.dumps(item))['userID'];
		return response_with(responses.SUCCESS_200, value={"value": item } );

@app.route("/addPost", methods=['POST'])
def addPost():
	loadMe = json.dumps(request.form)
	postInfo = json.loads(loadMe)
	try:
		response = dynamodb.Table("195PostsTable").put_item(
				Item={
						'postID' : sha256encrypt(postInfo["city"]+postInfo["name"]),
						'city' : postInfo["city"].lower(),
						'name' : postInfo["name"].lower(),
						'date' : postInfo["date"].lower(),
						'time' : postInfo["time"].lower(),
						'description' : postInfo["description"].lower(),
						'userID' : postInfo['userID'].lower()
						# 'coordinates' : postInfo["coordinates"] #format: (lat, long)
 				}
			)
	except Exception as e:
		return response_with(responses.INVALID_FIELD_NAME_SENT_422, value={"value": str(e)})
	else:
		return response_with(responses.SUCCESS_200, value={"value" : "success"});

@app.route("/getPosts", methods=['GET'])
def testscan():
	city = str(request.args.get('city'));
	fe = Key('city').eq(city)
	response = dynamodb.Table("195PostsTable").scan( FilterExpression = fe );
	return jsonify(response["Items"]);

################################################################################################################################################
################################################################################################################################################
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
