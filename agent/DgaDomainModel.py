import datetime

from DgaDomainDAO import DgaDomainDAO


class DgaDomainModel:

    def __init__(self, ip, domain="n/a", dga=False, date=str(datetime.date.today())):
        self.ip = ip
        self.dominio = domain
        self.dga = dga
        self.fecha = date
        self.DgaDomainDAO = DgaDomainDAO(ip, domain, dga, date)

    def isActive(self):
        active = False
        if self.DgaDomainDAO.exists():
            active = self.DgaDomainDAO.isActive(True)

        return active

    def exists(self):
        exists = False
        if self.DgaDomainDAO.exists():
            exists = True

        return exists

    def createDgaDomain(self):
        created = False
        if not self.DgaDomainDAO.exists():
            self.DgaDomainDAO.create()
            created = True

        return created

    def read(self):
        read = False
        if self.DgaDomainDAO.exists():
            dgaDomain = self.DgaDomainDAO.read(self.ip)
            self.dominio = dgaDomain[1]
            self.dga = dgaDomain[2]
            self.fecha = dgaDomain[3]
            read = True

        return read