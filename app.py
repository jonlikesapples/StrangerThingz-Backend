from flask import Flask, jsonify
import json
import requests
from firebase import firebase
app = Flask(__name__)


#https://github.com/ozgur/python-firebase
fb = firebase.FirebaseApplication('https://stranger-things-ce12a.firebaseio.com/', None)

#get from firebase server
@app.route("/", methods=['GET'])
def get():
	queryResult = fb.get('/users', None) #returns a type List
	jsonresult = jsonify(queryResult) #jsonify it
	return jsonresult

@app.route('/post')
def redirect():
	return "please go to /post/<param>"

@app.route("/post/<param>",)
def post(param):
	posted = fb.post('/users', param)
	key = posted["name"] #key for posted thing
	return param + " was posted."

@app.route("/delete")
def delete():
	KEY = "2" 
	return fb.delete('/users', KEY)

if __name__ == '__main__':
    app.run(debug=True)