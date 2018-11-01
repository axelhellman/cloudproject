from flask import Flask
from celery import Celery
from subprocess import call
import sys, os, time
import json
import re
from os import environ as env

from  novaclient import client
import keystoneclient.v3.client as ksclient
from keystoneauth1 import loading
from keystoneauth1 import session
#this is the argument for the broker
#app = Celery('tasks', broker='pyamqp://guest@localhost//')
app = Celery('tasks', backend='rpc://', broker='pyamqp://guest@localhost')
#amount_of_workers = 0
#startcluster=False

@app.task
def removespark(SW, CW):
    # Remove sparkmaster
    name = "acc20-sparkmaster"
    if not removeinstance(name):
        print "Error while deleting cluster (problem deleting the master)"

    # Remove sparkworkers
    while amount_of_workers > 0
        name = "acc20-sparkworker"+str(amount_of_workers)
        if removeinstance(name):
            amount_of_workers -= 1
        else:
            print "Error while deleting cluster (problem deleting one of the workers)"
            break

@app.task
def removeinstance(name):
    if name exists:
        nova delete name
        print "Delete instance with name: " + name
        return True
    else:
        print "There's no instance with name: " + name
        return False




@app.task
def resizespark(SW, CW):
    SW=int(SW)
    CW=int(CW)
    diff = SW-CW
    if diff==0:
        print("You already have that amount fo workers")
    elif diff>0:
        #adding workers
        while amount_of_workers <= SW:
            image_name = "acc20-S-important"
            name = "acc20-sparkworker"+str(amount_of_workers)
            createinstance(image_name,name, False)
            amount_of_workers+=1

    elif diff<0:
        #removing workers
        print("Remove workers")
