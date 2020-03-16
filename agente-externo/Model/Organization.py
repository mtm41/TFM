from DAO.OrganizationDAO import OrganizationDAO


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
