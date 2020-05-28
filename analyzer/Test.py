from datetime import datetime

from TestDAO import TestDAO


class Test:

    def __init__(self, serviceIp, servicePort, organization, id='undefined', name='undefined', type='undefined', analysisTime='undefined', endDate='undefined', state='undefined',
                 description='undefined', advice='undefined'):
        self.id = id
        self.name = name
        self.type = type
        self.analysisTime = analysisTime
        self.endDate = endDate
        self.state = state
        self.description = description
        self.advice = advice
        self.serviceIp = serviceIp
        self.servicePort = servicePort
        self.organization = organization
        self.testDAO = TestDAO(name, type, analysisTime, endDate, state, description, advice, serviceIp, servicePort, organization)

    def create(self):
        self.testDAO.create()

    def update(self):
        return False

    def delete(self):
        self.testDAO.delete(self.id)

    def read(self, timestamp):
        tests = []
        tests_tuples = self.testDAO.read(self.serviceIp, self.servicePort, self.organization, timestamp)

        for test_tuple in tests_tuples:
            test = Test(test_tuple[8], test_tuple[9], test_tuple[10], test_tuple[0], test_tuple[1], test_tuple[2],
                        test_tuple[3], test_tuple[4], test_tuple[5], test_tuple[6], test_tuple[7])
            tests.append(test)

        return tests
