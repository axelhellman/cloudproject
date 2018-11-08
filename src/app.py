#!flask/bin/python
from flask import Flask, jsonify, render_template, request
from tf import createspark, resizespark, removespark, sendFile, getTokens, startqtl
import subprocess
import sys
import os

app = Flask(__name__)
#current_workers = 0
UPLOAD_FOLDER = '/home/ubuntu/'


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html")

@app.route('/create', methods=['POST', 'GET'])
def create():
    amount = request.form['amount-workers']
    mess = " Started your cluster with " + amount + " workers..."
    print (mess)
    res = createspark.delay(True,amount)
    token = res.get()
    touser = "Your cluster is up, here is your token: " + str(token)
    return render_template("home.html", message=touser)

@app.route('/resize', methods=['POST', 'GET'])
def resize():
    amount = request.form['new-amount-workers']
    mess = "Resized your cluster to " + amount + " workers..."
    print (mess)
    res = resizespark.delay(amount)
    result = res.get()
    return render_template("home.html", message=mess)

@app.route('/remove', methods=['POST', 'GET'])
def remove():
    mess = "Your cluster has been removed"
    print (mess)
    res = removespark.delay()
    result = res.get()
    return render_template("home.html", message=mess)

@app.route('/inject', methods=['POST', 'GET'])
def inject():
    if request.method == 'POST':
        if 'file' not in request.files:
            mess = "File error"
            return render_template("home.html", message=mess)
        file = request.files['file']
        if file.filename == '':
            return render_template("home.html", message='No selected file')
        file.save('/home/ubuntu/' + file.filename)
        #This is how you're supposed to do it but for some reason it doesn't work: file.save(os.path.join(app.config[UPLOAD_FOLDER], file.filename))
        mess = str(file.filename) + " is injected: "

        res = sendFile.delay(file.filename)
        result = res.get()

        # Send it to spark master node
        # bashCommand = "scp " + '/home/ubuntu/'+file.filename + " sparkmaster:/home/ubuntu/test"
        # process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        # output, error = process.communicate()
        return render_template("home.html", message=mess)

@app.route('/jupyter', methods=['POST', 'GET'])
def jupyter():
    print "Running jupyter deployment script..."
    result = startqtl.delay()
    print "Jupyter deployment DONE"
    res = result.get()

    print "Obtaining the tokens..."
    result1 = getTokens.delay()
    mess = result1.get()
    #mess ="Hello use this ip: and this token:%s" %(token)
    return render_template("home.html", message=mess)


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False)