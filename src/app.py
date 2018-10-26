#!flask/bin/python
from flask import Flask, jsonify, render_template
from tf import createsparkworker
import subprocess
import sys

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
	return render_template("home.html")

@app.route('/start', methods=['GET','POST'])
def start():
	return render_template("start.html")

@app.route('/create', methods=['POST'])
def create():
    #user_message = "Starting your cluster... hold on :)"
    #render_template("home.html")
    res = createsparkworker.delay()
    result=res.get()
    #user_message = "Starting your cluster... hold on :)"
    #return render_template("start.html") #, user_message)
    return jsonify(result)

    #res = count.delay()
    #result = res.get()
    #return jsonify(result)



@app.route('/resize', methods=['GET','POST'])
def resize():
	return render_template("resize.html")

@app.route('/remove', methods=['GET','POST'])
def remove():
	return render_template("remove.html")


if __name__ == '__main__':
        app.run(host='0.0.0.0',debug=False)
