from flask import Flask, jsonify
import json
import pyrebase

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

#get from firebase server
@app.route("/", methods=['GET'])
def get():
	# queryresult = db.child("users").get().val() #type orderedDict
	# data = json.loads(json.dumps(queryresult)) #type (regular) dict
	# stringdata = json.dumps(data) #type string, no real use for this
	QUERY_RESULT = ""
	dbresult = db.child("users").get() #type orderedDict
	for user in dbresult.each(): 
		QUERY_RESULT += "key: " + user.key() + " " + "val: " + user.val() + "\n"
	return QUERY_RESULT

@app.route('/post')
def redirect():
	data = {"name": "Mortimer 'Morty' Smith"}
	db.child("users").push(data)
	return "hi"

@app.route("/post/<param>",)
def post(param):
	
	return key
	#return param + " was posted."

@app.route("/delete")
def delete():

	return 

if __name__ == '__main__':
    app.run(debug=True)