import base64
import datetime
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask
from flask import jsonify
from flask import Response
from flask import request

from Model.Organization import Organization
from Model.Service import Service
from Report import Report


app = Flask(__name__)

@app.route('/')
def get():
    return 'Hello World! This service has the objective of performing periodical vulnerability analysis on remote systems'

@app.route('/api/<key>/report/<timestamp>', methods=['GET'])
def getReport(key, timestamp):
    org = Organization()
    if org.authenticate(key):
        report = Report(timestamp, org.name)
        report_json = report.generate()

        return jsonify(report_json)
    else:
        return Response("NOT AUTHORIZED", status=403)

#POST
@app.route('/api/alert/<base64ip>', methods=['POST'])
def sendLocalAlert(base64ip):
    base64IpBytes = base64ip.encode('ascii')
    message_bytes = base64.b64decode(base64IpBytes)
    ip_address = message_bytes.decode('ascii')

    api_key = str(request.form.get('key'))
    organization = Organization()
    print(api_key)
    if organization.authenticate(api_key):
        print('ENTRA')
        localReport = str(request.form.get('alert'))
        if sendReportToUser(organization.email, localReport, ip_address, True):
            return Response("Alert sent", status=200)
        else:
            return Response("Error sending alert", status=500)
    else:
        return Response("NOT AUTHORIZED", status=403)


#POST
@app.route('/api/report/<base64ip>', methods=['POST'])
def sendLocalReport(base64ip):
    base64IpBytes = base64ip.encode('ascii')
    message_bytes = base64.b64decode(base64IpBytes)
    ip_address = message_bytes.decode('ascii')

    api_key = str(request.form.get('key'))
    organization = Organization()
    print(api_key)
    if organization.authenticate(api_key):
        print('ENTRA')
        localReport = str(request.form.get('report'))
        if sendReportToUser(organization.email, localReport, ip_address, False):
            return Response("Report sent", status=200)
        else:
            return Response("Error sending report", status=500)
    else:
        return Response("NOT AUTHORIZED", status=403)

def sendReportToUser(email, localReport, ip, alert):
    sent = True
    try:
        gateway = smtplib.SMTP(host='smtp.gmail.com', port=587)
        gateway.starttls()
        gateway.login('auto.diagnose.tool.tfm@gmail.com', 'Eyg7JgGKY3FMFbH')

        msg = MIMEMultipart('alternative')
        msg['From'] = 'auto.diagnose.tool.tfm@gmail.com'
        msg['To'] = email
        subject = 'Daily Report for local host {}'.format(ip)
        if alert:
            subject = 'Alert happened in local host {}'.format(ip)
        msg['Subject'] = subject

        msg.attach(MIMEText(localReport, 'html'))

        gateway.send_message(msg)
    except Exception as ex:
        print(ex)
        sent = False

    return sent

#POST
@app.route('/api/tool/<base64ip>', methods=['POST'])
def beginWorkingDay(base64ip):
    now = datetime.datetime.now().strftime('%H:%M')

    print(now)
    base64IpBytes = base64ip.encode('ascii')
    message_bytes = base64.b64decode(base64IpBytes)
    ip_address = message_bytes.decode('ascii')

    api_key = str(request.form.get('key'))
    state = str(request.form.get('state'))

    if state == 'start' or state == 'end':
        organization = Organization()
        if organization.authenticate(api_key):
            organization.checkSchedule(ip_address, now, state)
            return Response("TIME UPDATED", status=200)
        else:
            return Response("NOT AUTHORIZED", status=403)
    else:
        return Response("BAD STATE", status=404)

#PUT
@app.route('/api/tool/<base64ip>', methods=['PUT'])
def updateWorkingDay(base64ip):
    now = datetime.datetime.now().strftime('%H:%M')
    state = 'update'
    base64IpBytes = base64ip.encode('ascii')
    message_bytes = base64.b64decode(base64IpBytes)
    ip_address = message_bytes.decode('ascii')

    api_key = str(request.form.get('key'))

    organization = Organization()
    if organization.authenticate(api_key):
        organization.checkSchedule(ip_address, now, state)
        return Response("TIME UPDATED", status=200)
        # restart Watcher
        # os.system('sudo systemctl restart watcher')
    else:
        return Response("NOT AUTHORIZED", status=403)

#PUT
@app.route('/api/service/<base64Service>', methods=['PUT'])
def changeTimeForServiceScan(base64Service):
    base64ServiceBytes = base64Service.encode('ascii')
    message_bytes = base64.b64decode(base64ServiceBytes)
    message = message_bytes.decode('ascii')

    ip = str(message).split('&', 1)[0]
    port = str(message).split('&', 1)[1]
    api_key = request.args.get('key')
    updatedTime = request.form.get('time')

    organization = Organization()
    organization.authenticate(api_key)
    serviceToChange = Service(organization.name, ip, port, 'undefined', updatedTime)
    lowest = serviceToChange.isLowestTimeRegistered()
    if serviceToChange.update():
        if lowest:
            #restart Watcher
            os.system('sudo systemctl restart watcher')
        resp = str('Time uptaded successfully to {}').format(updatedTime)
        return jsonify({'Message': resp})

    return jsonify({'Message': 'Service not found or same time was given'})

#DELETE
@app.route('/api/<key>/service/<base64Service>', methods=['DELETE'])
def deleteServiceScan(key, base64Service):
    base64ServiceBytes = base64Service.encode('ascii')
    message_bytes = base64.b64decode(base64ServiceBytes)
    message = message_bytes.decode('ascii')

    ip = str(message).split('&', 1)[0]
    port = str(message).split('&', 1)[1]

    organization = Organization()
    organization.authenticate(key)

    serviceToDelete = Service(organization.name, ip, port)
    if serviceToDelete.delete():
        resp = str('Service at port {} has been successfully deleted').format(port)
        return jsonify({'Message': resp})

    return jsonify({'Message': 'Service not found or an error happened while deletion was performed'})


@app.route('/api/<key>/organization/<organization>', methods=['DELETE'])
def deleteOrganization(key, organization):
    base64OrganizationBytes = organization.encode('ascii')
    message_bytes = base64.b64decode(base64OrganizationBytes)
    message = message_bytes.decode('ascii')

    organizationForKey = Organization()
    organizationForKey.authenticate(key)

    if organizationForKey.name == message:
        if organizationForKey.delete():
            resp = str('Organization {} has been successfully deleted').format(message)
            return jsonify({'Message': resp})

    return jsonify({'Message': 'Deletion was not performed'})
