from flask import Flask
from celery import Celery
import sys, os
import json
import re
#this is the argument for the broker
#app = Celery('tasks', broker='pyamqp://guest@localhost//')
app = Celery('tasks', backend='rpc://', broker='pyamqp://guest@localhost')


@app.task
def count():

        words = ['han', 'hon', 'den', 'det', 'denne', 'denna', 'hen']
   
        dictword= {}        
        for word in words:
            dictword[word] = 0

        path = "./data2"
        for filename in os.listdir(path):
            filepath = path+"/"+filename

            with open (filepath) as jf:
                for line in jf:
                    try:
                        tweet = json.loads(line)
                    except ValueError:
                        continue
                    if('retweeted_status' in tweet):
                        continue
                    else:
                        regex = [r'\bhan\b', r'\bhon\b', r'\bden\b', r'\bdet\b', r'\bdenne\b', r'\bdenna\b', r'\bhen\b']
                        
                        text = tweet['text']
                        
                        for x in regex:
                            found = re.findall(x, text, re.IGNORECASE)
                            if found:
                                dictword[x[2:-2]]+=1
                        

        return (dictword)