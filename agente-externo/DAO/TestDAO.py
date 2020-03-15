from DatabaseConnection import DatabaseConnection
from Model.Test import Test


class TestDAO:
    def __init__(self, name, type, initDate, endDate, state, description, advice, serviceIP, servicePort):
        self.name = name
        self.type = type
        self.initDate = initDate
        self.endDate = endDate
        self.state = state
        self.description = description
        self.advice = advice
        self.serviceIp = serviceIP
        self.servicePort = servicePort

    def create(self):
        conn = DatabaseConnection().conn
        cur = conn.cursor()

        sql = "INSERT INTO Prueba(nombre, tipo, fechaInicio, fechaFin, estado, descripcion, consejo,  servicioIP, " \
              "servicioPuerto) VALUES (?,?,?,?,?,?,?,?,?)"
        data_tuple = (self.name, self.type, self.initDate, self.endDate, self.state,
                      self.description, self.advice, self.serviceIp, self.servicePort)

        cur.execute(sql, data_tuple)
        conn.commit()

        conn.close()

    def update(self):
        return False

    def delete(self, id):
        conn = DatabaseConnection().conn
        cur = conn.cursor()

        sql = "DELETE FROM Prueba WHERE ID=?"
        cur.execute(sql, id)
        conn.commit()

        conn.close()
        return True

    def read(self, id):
        organization = None
        conn = DatabaseConnection().conn
        cur = conn.cursor()

        sql = "SELECT * FROM Prueba WHERE ID=?"
        cur.execute(sql, id)
        resultSet = cur.fetchone()

        if resultSet is not None:
            organization = Test(resultSet[0], resultSet[1], resultSet[2], resultSet[3], resultSet[4], resultSet[5],
                                resultSet[6], resultSet[7], resultSet[8], resultSet[9])

        return organization
