from DatabaseConnection import DatabaseConnection
from Model.Service import Service


class ServiceDAO:
    def __init__(self, ip, port, tech, timeAnalysis, organization):
        self.ip = ip
        self.port = port
        self.tech = tech
        self.timeAnalysis = timeAnalysis
        self.organization = organization

    def create(self):
        conn = DatabaseConnection().conn
        cur = conn.cursor()

        sql = "INSERT INTO Service(ip, puerto, tecnologia, horaAnalisis, organizacion)" \
              "VALUES (?,?,?,?,?)"
        data_tuple = (self.ip, self.port, self.tech, self.timeAnalysis, self.organization)

        cur.execute(sql, data_tuple)
        conn.commit()

        conn.close()

    def update(self):
        return False

    def delete(self, ip, port):
        conn = DatabaseConnection().conn
        cur = conn.cursor()

        sql = "DELETE FROM Servicio WHERE ip=? AND port=?"
        data_tuple = (self.ip, self.port)
        cur.execute(sql, data_tuple)
        conn.commit()

        conn.close()
        return True

    def read(self, ip, port):
        service = None
        conn = DatabaseConnection().conn
        cur = conn.cursor()

        sql = "SELECT * FROM Servicio WHERE ip=? AND port=?"
        data_tuple = (ip, port)
        cur.execute(sql, data_tuple)
        resultSet = cur.fetchone()

        if resultSet is not None:
            service = Service(resultSet[0], resultSet[1], resultSet[2], resultSet[3], resultSet[4])

        return service

