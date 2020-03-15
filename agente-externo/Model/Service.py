from DAO.ServiceDAO import ServiceDAO


class Service:

    def __init__(self, organization, ip='undefined', port='undefined', technology='undefined', analysisTime='undefined'):
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
        service_data = self.serviceDAO.read(self.ip, self.port)
        self.ip = service_data[0]
        self.port = service_data[1]
        self.technology = service_data[2]
        self.analysisTime = service_data[3]
        self.organization = service_data[4]

        return self

    def readByOrganization(self):
        services = []
        services_data = self.serviceDAO.readByOrganization(self.organization)

        for service in services_data:
            services.append(Service(service[4], service[0], service[1], service[2], service[3]))

        return services
