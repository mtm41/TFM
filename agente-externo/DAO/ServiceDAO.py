from DatabaseConnection import DatabaseConnection


class ServiceDAO:
    def __init__(self, ip, port, tech, timeAnalysis, organization):
        self.ip = ip
        self.port = port
        self.tech = tech
        self.timeAnalysis = timeAnalysis
        self.organization = organization

    def create(self):
        conn = DatabaseConnection().conn
        try:
            cur = conn.cursor()

            sql = "INSERT INTO Servicio(ip, puerto, tecnologia, horaAnalisis, organizacion)" \
                  "VALUES (%s,%s,%s,%s,%s)"
            data_tuple = (self.ip, self.port, self.tech, self.timeAnalysis, self.organization)

            cur.execute(sql, data_tuple)
            conn.commit()
        finally:
            conn.close()

    def checkLowest(self):
        conn = DatabaseConnection().conn
        lowest = False
        try:
            cur = conn.cursor()

            sql = "SELECT horaAnalisis FROM Servicio ORDER BY horaAnalisis Limit 1"
            cur.execute(sql)
            resultSet = cur.fetchone()

            if resultSet is not None:
                lowestTime = resultSet[0]
                if lowestTime == self.timeAnalysis:
                    lowest = True
        finally:
            cur.close()
            conn.close()

        return lowest

    def update(self):
        conn = DatabaseConnection().conn
        updated = False
        try:
            cur = conn.cursor()

            sql = "UPDATE Servicio SET horaAnalisis=%s WHERE ip=%s AND puerto=%s AND organizacion=%s"
            data_tuple = (self.timeAnalysis, self.ip, self.port, self.organization)

            print(data_tuple)
            cur.execute(sql, data_tuple)
            if cur.rowcount > 0:
                updated = True
            conn.commit()
        except:
            print('UPDATE SERVICE ERROR')
        finally:
            conn.close()
        return updated

    def delete(self, ip, port, organization):
        conn = DatabaseConnection().conn
        deleted = False
        try:
            cur = conn.cursor()
            print('Intentando borrar')
            print(ip)
            print(port)
            print(organization)
            sql = "DELETE FROM Servicio WHERE ip=%s AND puerto=%s AND organizacion=%s"
            data_tuple = (ip, port, organization)
            cur.execute(sql, data_tuple)

            if cur.rowcount > 0:
                print('DELETED')
                deleted = True

            conn.commit()
        except Exception as ex:
            print(ex)
            deleted = False
        finally:
            conn.close()

        return deleted

    def read(self, ip, port, organizacion):
        service = None
        conn = DatabaseConnection().conn
        cur = conn.cursor()

        sql = "SELECT * FROM Servicio WHERE ip=%s AND puerto=%s AND organizacion=%s"
        data_tuple = (ip, port, organizacion)
        cur.execute(sql, data_tuple)
        resultSet = cur.fetchone()

        if resultSet is not None:
            service = (resultSet[0], resultSet[1], resultSet[2], resultSet[3], resultSet[4])

        conn.close()
        return service

    def readByOrganization(self, organization):
        services = []
        conn = DatabaseConnection().conn
        cur = conn.cursor()

        sql = "SELECT * FROM Servicio WHERE organizacion=%s"
        data_tuple = (organization,)
        cur.execute(sql, data_tuple)
        row = cur.fetchone()

        while row is not None:
            service = (row[0], row[1], row[2], row[3], row[4])
            services.append(service)
            row = cur.fetchone()

        return services
