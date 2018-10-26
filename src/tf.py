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
amount_of_workers = 0
startcluster=False
@app.task
def resizespark(SW):
    SW=int(SW)
    diff = amount_of_workers-SW
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
    
@app.task
def createspark(SM, SW):
    if (startcluster==False):
        startcluster=True
        SW=int(SW)
        amount_of_workers=SW
        i=1
        if SM == True:
            image_name = "acc20-SM-important" # acc20-SM-important
            name = "acc20-sparkmaster"
            createinstance(image_name,name,True)

        while i <= SW:
            image_name = "acc20-S-important"
            name = "acc20-sparkworker"+str(i)
            createinstance(image_name,name, False)
            i+=1
        else: 
            print("There is already a cluster running, you can either resize or decomission the cluster")


def createinstance(image_name, name, assign_fip):
    flavor = "ACCHT18.normal"
    private_net = "SNIC 2018/10-30 Internal IPv4 Network"
    floating_ip_pool_name = None #"Public External IPv4 network"
    floating_ip = None

    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(auth_url=env['OS_AUTH_URL'],
        username=env['OS_USERNAME'],
        password=env['OS_PASSWORD'],
        project_name=env['OS_PROJECT_NAME'],
        project_domain_name=env['OS_USER_DOMAIN_NAME'],
        project_id=env['OS_PROJECT_ID'],
        user_domain_name=env['OS_USER_DOMAIN_NAME'])

    sess = session.Session(auth=auth)
    nova = client.Client('2.1', session=sess)
    print "user authorization completed."

    image = nova.glance.find_image(image_name)

    flavor = nova.flavors.find(name=flavor)

    if private_net != None:
        net = nova.neutron.find_network(private_net)
        nics = [{'net-id': net.id}]
    else:
        sys.exit("private-net not defined.")

#print("Path at terminal when executing this file")
#print(os.getcwd() + "\n")
    cfg_file_path =  os.getcwd()+'/cloud-cfg.txt'
    if os.path.isfile(cfg_file_path):
        userdata = open(cfg_file_path)
    else:
        sys.exit("cloud-cfg.txt is not in current working directory")

    secgroups = ['default', 'kramstrom-lab1'] #add the security group we need to have for SparkMaster, SparkWorker and Ansible-Node

    print "Creating instance ... "
    instance = nova.servers.create(name=name, image=image, flavor=flavor, userdata=userdata, nics=nics,security_groups=secgroups) #key_name='axel_keypair_uu')
    inst_status = instance.status
    print "waiting for 10 seconds.. "
    time.sleep(10)

    while inst_status == 'BUILD':
        print "Instance: "+instance.name+" is in "+inst_status+" state, sleeping for 5 seconds more..."
        time.sleep(5)
        instance = nova.servers.get(instance.id)
        inst_status = instance.status

    return "Instance: "+ instance.name +" is in " + inst_status + "state"

    #if assign_fip == True:
    #    instance.add_floating_ip("")#insert floating ip
