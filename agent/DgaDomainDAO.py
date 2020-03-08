import datetime

from DatabaseConnection import DatabaseConnection


class DgaDomainDAO:

    def __init__(self, ip, domain="n/a", dga=False, date=str(datetime.date.today())):
        self.ip = ip
        self.dominio = domain
        self.dga = dga
        self.fecha = date

    def create(self):
        conn = DatabaseConnection(DatabaseConnection.dbFile).conn
        cur = conn.cursor()

        sql = "INSERT INTO DgaDomain(ip, dominio, dga, fecha) VALUES(?,?,?,?)"
        dga = int(self.dga == 'true')
        print('Insert')
        data_tuple = (self.ip, self.dominio, dga, self.fecha)
        print(data_tuple)
        cur.execute(sql, data_tuple)
        conn.commit()
        print('Insert1')
        lastId = cur.lastrowid

        conn.close()
        return lastId

    def isActive(self, date):
        active = False
        conn = DatabaseConnection(DatabaseConnection.dbFile).conn
        cur = conn.cursor()

        sql = "SELECT * FROM DgaDomain WHERE ip=?"
        dateToday = datetime.datetime.utcnow()
        dateTomorrow = datetime.date.today() + datetime.timedelta(days=1)
        if date:
            inferiorLimit = " AND fecha >= Datetime('{}-{}-{} 00:01:00')".format(dateToday.year, dateToday.month,
                                                                                 dateToday.day)
            superiorLimit = " AND fecha <= Datetime('{}-{}-{} 23:59:00')".format(dateTomorrow.year, dateTomorrow.month,
                                                                                 dateTomorrow.day)
            sql += inferiorLimit
            sql += superiorLimit
        resultSet = cur.execute(sql, (self.ip,))

        if resultSet.rowcount > 0:
            active = True

        conn.close()
        return active

    def exists(self):
        conn = DatabaseConnection(DatabaseConnection.dbFile).conn
        cur = conn.cursor()

        exists = False
        sql = "SELECT * FROM DgaDomain WHERE ip=?"
        cur.execute(sql, (self.ip,))
        resultSet = cur.fetchone()

        if resultSet is not None:
            exists = True

        conn.close()
        print(exists)
        return exists

    def read(self, ip):
        conn = DatabaseConnection(DatabaseConnection.dbFile).conn
        cur = conn.cursor()

        sql = "SELECT * FROM DgaDomain WHERE ip='%s" % ip
        resultSet = cur.execute(sql)

        dgaDomain = resultSet.next()
        if dgaDomain:
            self.ip = dgaDomain[0]
            self.dominio = dgaDomain[1]
            self.dga = dgaDomain[2]
            self.fecha = dgaDomain[3]

        conn.close()
        return dgaDomain

