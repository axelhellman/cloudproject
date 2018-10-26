#!flask/bin/python
from flask import Flask, jsonify, render_template, request
from tf import createspark
import subprocess
import sys

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
        return render_template("home.html")

@app.route('/create', methods=['POST'])
def create():
        amount = request.form['amount-workers']
        user_mess = "Starting your cluster with " + amount + " workers..."
        print user_mess
        res = createspark.delay(True,amount)
        result=res.get()
        render_template("home.html", message=user_mess)
        return jsonify(result)

@app.route('/resize', methods=['POST'])
def resize():
		amount = request.form['new-amount-workers']
		user_mess = "Resizing your cluster with" + amount + " workers..."
		print user_mess
		render_template("home.html", message=user_mess)
        return render_template("home.html", message=user_mess)

@app.route('/remove', methods=['POST'])
def remove():
		user_mess = "Removes your cluster..."
		print user_mess
        return render_template("home.html")


if __name__ == '__main__':
        app.run(host='0.0.0.0',debug=False)
