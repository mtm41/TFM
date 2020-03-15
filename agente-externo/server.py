from flask import Flask

app = Flask(__name__)

@app.route('/')
def get():
    return 'Hello World!'

@app.route('/api/<key>/report/<timestamp>', methods=['GET'])
def getReport(key, timestamp):
    return 'User has asked for report created at %s' % timestamp

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
