from DAO.ServiceDAO import ServiceDAO


class Service:

    def __init__(self, ip, port, technology, analysisTime, organization):
        self.ip = ip
        self.port = port
        self.technology = technology
        self.analysisTime = analysisTime
        self.organization = organization
        self.serviceDAO = ServiceDAO(ip, port, technology, analysisTime, organization)

    def create(self):
        self.serviceDAO.create()

    def update(self):
        return False

    def delete(self):
        self.serviceDAO.delete(self.ip, self.port)

    def read(self):
        return self.serviceDAO.read(self.ip, self.port)
