import time

from DAO.OrganizationDAO import OrganizationDAO
from Model.Service import Service
from Model.Test import Test


class Organization:

    def __init__(self, name='undefined', tel='undefined', description='undefined', analysisTime='undefined', email='undefined'):
        self.name = name
        self.tel = tel
        self.description = description
        self.analysisTime = analysisTime
        self.email = email
        self.organizationDAO = OrganizationDAO(name, tel, description, analysisTime, email)

    def create(self):
        self.organizationDAO.create()

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
                    if toolStartedTime < scheduleInit or toolStartedTime > scheduleEnd:
                        print('AVISO, SE HA INICIADO EN UNA HORA PROHIBIDA')
                    service.delete() # We take advantage of On delete cascade option to delete Tests
                    service.analysisTime = self.sumIntervalTime(toolStartedTime.split(':'))
                    service.create()
                elif state == 'end':
                    if scheduleInit < toolStartedTime < scheduleEnd:
                        print('AVISO, SE HA ACTUALIZADO EN UNA HORA PROHIBIDA')
                    service.analysisTime = scheduleInit
                    service.update()
                    test = Test(ip, 0, self.name, 'undefined', 'Monitoring', toolStartedTime, toolStartedTime, 0, 'Local machine has stopped monitoring tool', 'Check if this is normal')
                    test.create()
                else:
                    if not (scheduleInit < toolStartedTime < scheduleEnd):
                        print('AVISO, SE HA APAGADO EN UNA HORA PROHIBIDA')
                    nextCheckTime = self.sumIntervalTime(toolStartedTime.split(':'))
                    service.analysisTime = nextCheckTime
                    service.update()
        else:
            service.create()

    def sumIntervalTime(self, toolStartedTime):
        rest = (toolStartedTime[1] + 39) % 60
        if rest > 0:
            toolStartedTime[0] = toolStartedTime[0] + 1
            toolStartedTime[1] = toolStartedTime[1] + rest
        else:
            toolStartedTime[0] = toolStartedTime[0]
            toolStartedTime[1] = toolStartedTime[1] + 39
        toolStartedTime = str('{}:{}').format(toolStartedTime[0], toolStartedTime[1])
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
                               organization_data[4])
        return org
