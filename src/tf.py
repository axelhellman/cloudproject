from flask import Flask
from celery import Celery
import subprocess
import sys, os, time
import json
import re
from os import environ as env

from  novaclient import client
import keystoneclient.v3.client as ksclient
from keystoneauth1 import loading
from keystoneauth1 import session

app = Celery('tasks', backend='rpc://', broker='pyamqp://guest@localhost')

current_workers=0
started_cluster = False

@app.task
def resizespark(SW):
    if started_cluster == True:
        global current_workers
        print current_workers

        SW=int(SW)
        diff = SW-current_workers
        if diff==0:
            print("You already have that amount fo workers")
        elif diff>0:
            #adding workers
            cw = current_workers
            cw +=1
            while cw <= SW:
                image_name = "acc20-S-important"
                name = "acc20-sparkworker"+str(cw)
                createinstance(image_name,name, False)
                cw+=1
            current_workers = SW
        elif diff<0:
            cw = current_workers
            print "Current workers: " + str(current_workers)
            #cw -=1
            while cw > SW and cw > 0:
                name = "acc20-sparkworker"+str(cw)
                print "Deleting " + name
                removeinstance(name)
                cw-=1
            current_workers = SW
            print("Remove workers")
       # bashCommand = "ansible-playbook -s spark_deployment.yml"
       # process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
       # output, error = process.communicate()
        
    else:
        print("There is not a cluster yet")


@app.task
def removeinstance(name):
    print ("trying to remove instance with name" + name)
    # if name exists:
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

    server = nova.servers.find(name=name)
    server.delete()
    #     print "Delete instance with name: " + name
    #     return True
    # else:
    #     print "There's no instance with name: " + name
    #     return False

@app.task
def removespark():
    global started_cluster
    global current_workers
    # Remove sparkmaster
    name = "acc20-sparkmaster"
    removeinstance(name)
    print "Removed sparkmaster"

    # Remove sparkworkers
    while current_workers > 0:
        name = "acc20-sparkworker"+str(current_workers)
        removeinstance(name)
        current_workers -= 1

    started_cluster = False

@app.task
def sendFile(fileName):
    # bashCommandSSH = 'ssh-keygen -f  \"/home/ubuntu/.ssh/known_hosts\" -R sparkmaster'
    # process = subprocess.Popen(bashCommandSSH.split(), stdout=subprocess.PIPE)
    # output, error = process.communicate()
    # print "ssh command done: " + bashCommandSSH


    # Send it to spark master node
    bashCommand = "scp -o StrictHostKeyChecking=no " + '/home/ubuntu/'+fileName + " sparkmaster:/home/ubuntu"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

@app.task()
def startqtl():
    bashCommand = "/home/ubuntu/changeHostIPs.sh"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    bashCommand = "ansible-playbook -s spark_deployment.yml"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

@app.task
def getTokens():
    bashCommand = "ssh -o StrictHostKeyChecking=no sparkmaster 'cat /home/ubuntu/.local/share/jupyter/runtime/*.json | grep token' > tokens"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    floatPath = os.getcwd()+'/floatingSM'
    tokensPath = os.getcwd()+'/tokens'

    if os.path.isfile(floatPath) and os.path.isfile(tokensPath):
        floatIP = open(floatPath, 'r')
        tokens = open(tokensPath, 'r')
        tokensContent = repr(tokens.read())
        floatIPContent = repr(floatIP.read())
        toUser = "Floating IP: " + floatIPContent + "Tokens: " + tokensContent
        return toUser
    else:
        return "FILE NOT FOUND"

@app.task
def createspark(SM, SW):
    global current_workers
    global started_cluster
    if (started_cluster==False):
        print started_cluster
        started_cluster = True
        SW=int(SW)
        current_workers = SW
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


    print SW
    print started_cluster

    # IPs
    time.sleep(5)
    bashCommand = "/home/ubuntu/changeHostIPs.sh"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()


def createinstance(image_name, name, assign_fip):
    flavor = "ACCHT18.normal"
    private_net = "SNIC 2018/10-30 Internal IPv4 Network"
    floating_ip_pool_name = None #"Public External IPv4 network"
    floating_ip = "130.238.29.94" #should be able take an IP from the pool which is free instead todo if we have time 

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

    if assign_fip:
        secgroups = ['default', 'ACC20SM'] #add the security group we need to have for SparkMaster, SparkWorker and Ansible-Node
    else:
        secgroups = ['default', 'ACC20S']

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
    
    if assign_fip == True:
        instance.add_floating_ip(floating_ip)#insert floating ip

    return "Instance: "+ instance.name +" is in " + inst_status + "state"