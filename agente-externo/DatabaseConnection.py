import mysql.connector as mariadb


class DatabaseConnection:
    conn = None

    def __init__(self):
        self.username = 'manuel'
        self.database = 'Analysis'
        self.port = '3306'
        self.conn = mariadb.connect(user=self.username, password='eljoker97', database=self.database)

    def close(self):
        if self.conn:
            self.close()
