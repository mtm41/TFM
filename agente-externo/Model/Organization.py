import base64
import datetime
import time

import server
from DAO.OrganizationDAO import OrganizationDAO
from Model.Service import Service
from Model.Test import Test


class Organization:

    def __init__(self, name='undefined', tel='undefined', description='undefined', analysisTime='undefined',
                 email='undefined', initSchedule='undefined', endSchedule=''):
        self.name = name
        self.tel = tel
        self.description = description
        self.analysisTime = analysisTime
        self.email = email
        self.initSchedule = initSchedule
        self.endSchedule = endSchedule
        self.organizationDAO = OrganizationDAO(name, tel, description, analysisTime, email)

    def create(self):
        self.organizationDAO.create()

    def isInTimeInterval(self, time, initInternal, endInterval):
        inInternal = -1
        hourTime = int(str(time).split(':')[0])
        minTime = int(str(time).split(':')[1])
        if int(str(initInternal).split(':')[0]) < hourTime < int(str(endInterval).split(':')[0]):
            inInternal = 1
        elif hourTime < int(str(initInternal).split(':')[0]):
            inInternal = 0
        elif hourTime > int(str(endInterval).split(':')[0]):
            inInternal = 2
        elif int(str(initInternal).split(':')[0]) == hourTime and minTime >= int(str(initInternal).split(':')[1]):
            inInternal = 1
        elif int(str(initInternal).split(':')[0]) == hourTime and minTime < int(str(initInternal).split(':')[1]):
            inInternal = 0
        elif hourTime == int(str(endInterval).split(':')[0]) and minTime >= int(str(endInterval).split(':')[1]):
            inInternal = 2
        elif int(str(endInterval).split(':')[0]) == hourTime and minTime < int(str(endInterval).split(':')[1]):
            inInternal = 1

        return inInternal



    def checkSchedule(self, ip, toolStartedTime, state):
        org = self.organizationDAO.read(self.name)
        scheduleInit = org[5]
        scheduleEnd = org[6]
        toolStartedTime = str(toolStartedTime).split(':')
        toolStartedTime = self.sumIntervalTime(toolStartedTime)
        service = Service(self.name, ip, 0, 'Monitoring', toolStartedTime)
        if service.read() is not None:
            if scheduleInit and scheduleEnd:
                if state == 'start':
                    if self.isInTimeInterval(toolStartedTime, scheduleInit, scheduleEnd) == 0 or self.isInTimeInterval(toolStartedTime, scheduleInit, scheduleEnd) == 2:
                        alert = 'AVISO! SE ACABA DE INICIAR EL EQUIPO EN UNA HORA PROHIBIDA'
                        server.sendReportToUser(self.email, alert, ip, True)
                    service.delete() # We take advantage of On delete cascade option to delete Tests
                    nextCheck = self.sumIntervalTime(toolStartedTime.split(':'))
                    service.analysisTime = str(nextCheck)
                    service.create()
                elif state == 'end':
                    if self.isInTimeInterval(toolStartedTime, scheduleInit, scheduleEnd) == 1:
                        alert = "AVISO! SE HA APAGADO LA HERRAMIENTA EN UNA HORA PROHIBIDA, POSIBLE INTENTO DE EVADIR DETECCIONES"
                        server.sendReportToUser(self.email, alert, ip, True)
                    service.analysisTime = scheduleInit
                    service.update()
                    test = Test(ip, 0, self.name, 'undefined', 'Monitoring', 'Monitoring', datetime.datetime.now(),
                                datetime.datetime.now(), 0, 'Local machine has stopped monitoring tool',
                                'Check if this is normal')
                    test.create()
                else:
                    if self.isInTimeInterval(toolStartedTime, scheduleInit, scheduleEnd) != 1:
                        alert = "AVISO! LA HERRAMIENTA SIGUE ACTIVA EN UNA HORA PROHIBIDA"
                        server.sendReportToUser(self.email, alert, ip, True)
                    nextCheckTime = self.sumIntervalTime(toolStartedTime.split(':'))
                    service.analysisTime = nextCheckTime
                    service.update()
        else:
            nextCheckTime = self.sumIntervalTime(toolStartedTime.split(':'))
            service.analysisTime = nextCheckTime
            service.create()

    def sumIntervalTime(self, toolStartedTime):
        hour = int(toolStartedTime[0])
        min = int(toolStartedTime[1])
        rest = (min + 39) / 60
        if rest >= 1:
            hour = hour + 1
            min = (min + 39) % 60
        else:
            hour = hour
            min = min + 39

        toolStartedTime = str('{}:{}').format(hour, min)
        return toolStartedTime

    def update(self):
        return False

    def delete(self):
        return self.organizationDAO.delete(self.name)

    # If OrganizationDAO object is initialized this method will search their associated key.
    # On the contrary, it will find any coincidente with api_key and returns data necessary to
    # instanciate Organization object
    def authenticate(self, api_key):
        authenticated = False
        organization_tuple = self.organizationDAO.obtainKey(api_key)

        if organization_tuple is not None:
            authenticated = True
            self.name = organization_tuple[0]
            self.tel = organization_tuple[1]
            self.description = organization_tuple[2]
            self.analysisTime = organization_tuple[3]
            self.email = organization_tuple[4]

        return authenticated

    def read(self):
        org = None
        organization_data = self.organizationDAO.read(self.name)
        if organization_data is not None:
            org = Organization(organization_data[0], organization_data[1], organization_data[2], organization_data[3],
                               organization_data[4], organization_data[5], organization_data[6])
        return org
    
    def readOrgWithService(self):
        keys = []
        organization_data = self.organizationDAO.readOrgWithServices()
        
        for row in organization_data:
            keys.append((row[0], row[1]))
        
        return keys
