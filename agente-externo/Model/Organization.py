from DAO.OrganizationDAO import OrganizationDAO


class Organization:

    def __init__(self, name, tel, description, analysisTime, email):
        self.name = name
        self.tel = tel
        self.description = description
        self.analysisTime = analysisTime
        self.email = email
        self.organizationDAO = OrganizationDAO(name, tel, description, analysisTime, email)

    def create(self):
        self.organizationDAO.create()

    def update(self):
        return False

    def delete(self):
        self.organizationDAO.delete()

    def read(self):
        return self.organizationDAO.read(self.name)
