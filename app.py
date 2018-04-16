from flask import Flask, jsonify, request
import os
import json
import pyrebase

'''
git add .
git commit -m "commit message"
git push heroku master
https://strangerthingz-backend.herokuapp.com
'''
app = Flask(__name__)

#https://github.com/thisbejim/Pyrebase

config = {
  "apiKey": "AIzaSyAb0csAFZDQoYIJrflFTuYAwx7rS1t3oYg",
  "authDomain": "stranger-things-ce12a.firebaseapp.com",
  "databaseURL": "https://stranger-things-ce12a.firebaseio.com/",
  "storageBucket": "stranger-things-ce12a.appspot.com",
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()

#get from firebase server.
@app.route("/")
def nothing():
	return "WELCOME TO STRANGER THINGS! <br> \
	possible endpoints: <br> /allusers <br> /post <br> /delete <br> /getcount <br> /addcount"

@app.route("/test")
def test():
	return "TEST"

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

@app.route('/getcount') #gets total count
def getcount():
	dbresult = db.child("totalnumofusers").get()
	QUERY_RESULT = ""
	getcount = 123
	for user in dbresult.each(): 
		QUERY_RESULT += "key: " + str(user.key()) + " " + "val: " + str(user.val()) + "<br>"
		getcount = user.val();
		break;
	return str(getcount);

@app.route('/addcount') #increments count by 1
def addcount():
	dbresult = db.child("totalnumofusers").get()
	QUERY_RESULT = ""
	newcount = 123
	for user in dbresult.each(): 
		QUERY_RESULT += "key: " + str(user.key()) + " " + "val: " + str(user.val()) + "<br>"
		newcount = user.val() + 1;
		break;

	addcount = {"count": newcount }
	dbresult = db.child("totalnumofusers").update(addcount);
	return "count was incremented by 1, see firebase console."


#Format: /foods?var1=value&var2=value2&...
@app.route('/post')
def redirect():
	value = str(request.args.get('testvalue'));
	postedvalue = {"name": value }
	#ALWAYS USE .UPDATE to post, will create a new key too
	#.update has to take in a JSON object.
	db.child("users").child("testaccount").update(postedvalue);
	return value;



@app.route("/update")
def post(param):
	return "nothing."

@app.route("/delete")
def delete():
	db.child("users").child("account2").remove()
	return "deleted"

if __name__ == '__main__':
    from os import environ;
    app.run(debug=True, host='0.0.0.0', port=int(environ.get("PORT", 5000)));

    