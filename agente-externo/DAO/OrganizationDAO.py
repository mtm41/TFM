from DatabaseConnection import DatabaseConnection
from Model.Organization import Organization


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

        sql = "INSERT INTO Organizacion(nombre, telefono, descripcion, horaAnalisis, email)" \
              "VALUES (?,?,?,?,?)"
        data_tuple = (self.name, self.tel, self.description, self.analysisTime, self.email)

        cur.execute(sql, data_tuple)
        conn.commit()

        conn.close()

    def update(self):
        return False

    def delete(self):
        conn = DatabaseConnection().conn
        cur = conn.cursor()

        sql = "DELETE FROM Organizacion WHERE nombre=?"
        cur.execute(sql, self.name)
        conn.commit()

        conn.close()
        return True

    def read(self, name):
        organization = None
        conn = DatabaseConnection().conn
        cur = conn.cursor()

        sql = "SELECT * FROM Organizacion WHERE nombre=?"
        cur.execute(sql, name)
        resultSet = cur.fetchone()

        if resultSet is not None:
            organization = Organization(resultSet[0], resultSet[1], resultSet[2], resultSet[3], resultSet[4])

        return organization