from DatabaseConnection import DatabaseConnection
#from Model.Organization import Organization


class OrganizationDAO:

    def __init__(self, name, tel, description, analysisTime, email):
        self.name = name
        self.tel = tel
        self.description = description
        self.analysisTime = analysisTime
        self.email = email

    def create(self):
        conn = DatabaseConnection().conn
        cur = conn.cursor()

        api_key = self.generateKey()

        sql = "INSERT INTO Organizacion(nombre, telefono, descripcion, horaAnalisis, email, apiKey)" \
              "VALUES (%s,%s,%s,%s,%s,%s)"
        data_tuple = (self.name, self.tel, self.description, self.analysisTime, self.email, api_key)

        cur.execute(sql, data_tuple)
        conn.commit()

        conn.close()

    def generateKey(self):
        return "AJDOH382U3JJD9U83J232UD923"

    def obtainKey(self, key):
        organization_tuple = None
        conn = DatabaseConnection().conn
        cur = conn.cursor()

        sql = "SELECT nombre, telefono, descripcion, horaAnalisis, email FROM Organizacion WHERE apiKey=%s"
        data_tuple = (key,)
        if self.name != 'undefined':
            sql += ' AND nombre=%s'
            data_tuple = (key, self.name)

        print(sql)
        cur.execute(sql, data_tuple)
        resultSet = cur.fetchone()

        if resultSet is not None:
            organization_tuple = (resultSet[0], resultSet[1], resultSet[2], resultSet[3], resultSet[4])

        return organization_tuple

    def update(self):
        return False

    def delete(self, name):
        conn = DatabaseConnection().conn
        deleted = False
        try:
            cur = conn.cursor()

            sql = "DELETE FROM Organizacion WHERE nombre=%s"
            cur.execute(sql, (name,))
            conn.commit()
            if cur.rowcount > 0:
                deleted = True
        except Exception as ex:
            print(ex)
            deleted = False
        finally:
            conn.close()

        return deleted

    def read(self, name):
        organization = None
        conn = DatabaseConnection().conn
        cur = conn.cursor()

        sql = "SELECT * FROM Organizacion WHERE nombre=%s"
        cur.execute(sql, (name,))
        resultSet = cur.fetchone()

        if resultSet is not None:
            organization = (resultSet[0], resultSet[1], resultSet[2], resultSet[3], resultSet[4], resultSet[5], resultSet[6])

        return organization