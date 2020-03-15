from flask import Flask

from Model.Organization import Organization
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
        print('REPORT OBTENIDO')
        report_json = report.generate()
        print(report_json)
        return 'User has asked for report created at %s' % timestamp
    else:
        return 'Not authorized'

#PUT
@app.route('/api/service/<service>', methods=['PUT'])
def changeTimeForServiceScan(service):
    return 'User has asked for change %s time scanning' % service

#DELETE
@app.route('/api/<key>/service/<service>', methods=['DELETE'])
def deleteServiceScan(key, service):
    return 'User has asked for delete %s scanning' % service

@app.route('/api/<key>/organization/<organization>', methods=['DELETE'])
def deleteOrganization(key, organization):
    return 'User %s has asked for delete his personal data' % organization
