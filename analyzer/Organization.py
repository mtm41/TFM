from OrganizationDAO import OrganizationDAO


class Organization:

    def __init__(self, name):
        self.name = name

    def getEmail(self):
        return OrganizationDAO().getEmail(self.name)