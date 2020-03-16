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
        return self.serviceDAO.update()

    def delete(self):
        return self.serviceDAO.delete(self.ip, self.port, self.organization)

    def read(self):
        service_data = self.serviceDAO.read(self.ip, self.port)

        return Service(service_data[0], service_data[1], service_data[2], service_data[3], service_data[4])

    def readByOrganization(self):
        services = []
        services_data = self.serviceDAO.readByOrganization(self.organization)

        for service in services_data:
            services.append(Service(service[4], service[0], service[1], service[2], service[3]))

        return services
