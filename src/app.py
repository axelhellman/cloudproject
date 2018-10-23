#!flask/bin/python
from flask import Flask, jsonify, render_template
from tf import count
import subprocess
import sys

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
	return render_template("home.html")

@app.route('/start', methods=['GET','POST'])
def start():
	return render_template("start.html")

@app.route('/create', methods=['GET'])
def create():
	#just a dummy fucntion for now will not work, just 
	res = count.delay()
	result = res.get()
	return jsonify(result)


@app.route('/resize', methods=['GET','POST'])
def resize():
	return render_template("resize.html")

@app.route('/remove', methods=['GET','POST'])
def remove():
	return render_template("remove.html")


if __name__ == '__main__':
        app.run(host='0.0.0.0',debug=False)

