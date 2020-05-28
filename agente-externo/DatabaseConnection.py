import mysql.connector as mariadb
import yaml

class DatabaseConnection:
    conn = None

    def __init__(self):
        conf = yaml.load(open('application.yml'))
        self.username = conf['database_credentials']['username']
        self.database = conf['database_credentials']['database']
        self.port = '3306'
        self.conn = mariadb.connect(host=conf['database_credentials']['host'], user=self.username, password=conf['database_credentials']['password'], database=self.database)

    def close(self):
        if self.conn:
            self.close()
