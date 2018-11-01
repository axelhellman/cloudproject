#!flask/bin/python
from flask import Flask, jsonify, render_template, request
from tf import createspark, resizespark
import subprocess
import sys

app = Flask(__name__)
#current_workers = 0



@app.route('/', methods=['GET', 'POST'])
def home():
    	return render_template("home.html")

@app.route('/create', methods=['POST', 'GET'])
def create():
        amount = request.form['amount-workers']
    	mess = " Started your cluster with " + amount + " workers..."
    	print mess
        res = createspark.delay(True,amount)
    	result=res.get()
    	return render_template("home.html", message=mess)

@app.route('/resize', methods=['POST', 'GET'])
def resize():
		amount = request.form['new-amount-workers']
		mess = "Resized your cluster to " + amount + " workers..."
		print mess
        res = resizespark.delay(amount)
        result = res.get() 
    	return render_template("home.html", message=mess)

@app.route('/remove', methods=['POST', 'GET'])
def remove():
		mess = "Your cluster has been removed"
		print mess
        res = removespark.delay()
        result = res.get()
    	return render_template("home.html", message=mess)


if __name__ == '__main__':
    	app.run(host='0.0.0.0',debug=False)
