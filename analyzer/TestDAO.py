from datetime import datetime

from DatabaseConnection import DatabaseConnection


class TestDAO:
    def __init__(self, name, type, initDate, endDate, state, description, advice, serviceIP, servicePort, organization):
        self.name = name
        self.type = type
        self.initDate = initDate
        self.endDate = endDate
        self.state = state
        self.description = description
        self.advice = advice
        self.serviceIp = serviceIP
        self.servicePort = servicePort
        self.organization = organization

    def create(self):
        conn = DatabaseConnection().conn
        cur = conn.cursor()

        sql = "INSERT INTO Prueba(nombre, tipo, fechaInicio, fechaFin, estado, descripcion, consejo,  servicioIP, " \
              "servicioPuerto, organizacion) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        data_tuple = (self.name, self.type, self.initDate, self.endDate, self.state,
                      self.description, self.advice, self.serviceIp, self.servicePort, self.organization)
        print(data_tuple)

        cur.execute(sql, data_tuple)
        conn.commit()

        conn.close()

    def update(self):
        return False

    def delete(self, id):
        conn = DatabaseConnection().conn
        cur = conn.cursor()

        sql = "DELETE FROM Prueba WHERE ID=%s"
        cur.execute(sql, id)
        conn.commit()

        conn.close()
        return True

    def read(self, serviceIP, servicePORT, organization, timestamp):
        tests = []
        conn = DatabaseConnection().conn
        cur = conn.cursor()

        sql = "SELECT * FROM Prueba WHERE servicioIP=%s AND servicioPuerto=%s AND organizacion=%s"
        cur.execute(sql, (serviceIP, servicePORT, organization))
        row = cur.fetchone()

        while row is not None:
            test = (row[0], row[1], row[2], row[3], row[4], row[5],
                 row[6], row[7], row[8], row[9], row[10])
            if self.executedInDate(test[3], timestamp):
                tests.append(test)
            row = cur.fetchone()

        return tests

    def executedInDate(self, plannedTime, timestamp):
        sameDay = False
        serviceStartUp = timestamp
        print(plannedTime)
        date = plannedTime

        if serviceStartUp.day == date.day and serviceStartUp.month == date.month and serviceStartUp.year == date.year:
            sameDay = True

        return sameDay