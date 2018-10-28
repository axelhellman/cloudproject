#!flask/bin/python
from flask import Flask, jsonify, render_template, request
from tf import createspark, resizespark
import subprocess
import sys

app = Flask(__name__)
current_workers = 0
startcluster=False


@app.route('/', methods=['GET', 'POST'])
def home():
        return render_template("home.html")

@app.route('/create', methods=['POST', 'GET'])
def create():
        amount = request.form['amount-workers']
        mess = " Starting your cluster with " + amount + " workers..."
        print mess
        #res = createspark.delay(True,amount)
        #result=res.get()
        return render_template("home.html", message=mess)
        #return jsonify(result)

@app.route('/resize', methods=['POST', 'GET'])
def resize():
		amount = request.form['new-amount-workers']
		mess = "Resizing your cluster with" + amount + " workers..."
		print mess
		render_template("home.html", message=mess)
        return render_template("home.html", message=mess)

@app.route('/remove', methods=['POST', 'GET'])
def remove():
		mess = "Removes your cluster..."
		print mess
        return render_template("home.html")


if __name__ == '__main__':
        app.run(host='0.0.0.0',debug=False)
