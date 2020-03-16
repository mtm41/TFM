import base64

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

#PUT
@app.route('/api/service/<base64Service>', methods=['PUT'])
def changeTimeForServiceScan(base64Service):
    base64ServiceBytes = base64Service.encode('ascii')
    message_bytes = base64.b64decode(base64ServiceBytes)
    message = message_bytes.decode('ascii')

    ip = str(message).split('&', 1)[0]
    port = str(message).split('&', 1)[1]
    api_key = request.args.get('key')
    updatedTime = request.args.get('time')

    organization = Organization()
    organization.authenticate(api_key)
    serviceToChange = Service(organization.name, ip, port, 'undefined', updatedTime)
    if serviceToChange.update():
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
