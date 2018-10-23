from flask import Flask
from celery import Celery
import sys, os
import json
import re
#this is the argument for the broker
#app = Celery('tasks', broker='pyamqp://guest@localhost//')
app = Celery('tasks', backend='rpc://', broker='pyamqp://guest@localhost')


@app.task
def start_qtl():
    #TODO: run the scc-instance-usedata
      