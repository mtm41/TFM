from DAO.TestDAO import TestDAO


class Test:

    def __init__(self, id, name, type, analysisTime, endDate, state, description, advice, serviceIp, servicePort):
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
        self.testDAO = TestDAO(id, name, type, analysisTime, endDate, state, description, advice, serviceIp, servicePort)

    def create(self):
        self.testDAO.create()

    def update(self):
        return False

    def delete(self):
        self.testDAO.delete(self.id)

    def read(self):
        return self.testDAO.read(self.id)