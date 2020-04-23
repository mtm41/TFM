# Python Watcher service for analyzer
import os
import subprocess
import time
from datetime import datetime

import mysql.connector as mariadb
from systemd.daemon import notify, Notification


class DatabaseConnection:
    conn = None

    def __init__(self):
        self.username = 'Watcher'
        self.database = 'Analysis'
        self.port = '3306'
        self.conn = mariadb.connect(user=self.username, password='watcher123', database=self.database)

    def close(self):
        if self.conn:
            self.close()


if __name__ == '__main__':
    print('Starting up...')

    notify(Notification.READY)

    while True:
        conn = None

        try:
            conn = DatabaseConnection().conn
            cur = conn.cursor()

            sql = 'SELECT ip, puerto, organizacion, horaAnalisis, domainName, tecnologia FROM Servicio ' \
                  'WHERE NOT EXISTS (SELECT * FROM Prueba WHERE Servicio.ip=Prueba.servicioIp AND Servicio.puerto=Prueba.servicioPuerto AND Servicio.organizacion=Prueba.organizacion ' \
                  'AND DATE_FORMAT(Prueba.fechaInicio, "%Y-%m-%d") = CURDATE()) ORDER BY horaAnalisis LIMIT 1;'
            #sql = "SELECT ip, puerto, organizacion, horaAnalisis, domainName FROM Servicio WHERE horaAnalisis > '{}' ORDER BY horaAnalisis Limit 1".format(datetime.now().__format__("%H:%M:%S"))
            cur.execute(sql)
            resultSet = cur.fetchone()

            sleep = 1000000

            ip = ''
            port = ''
            organization = ''
            timeForAnalysis = ''
            domain = ''
            tecnologia = ''
            if resultSet is not None:
                ip = resultSet[0]
                port = resultSet[1]
                organization = resultSet[2]
                timeForAnalysis = resultSet[3]
                domain = resultSet[4]
                tecnologia = resultSet[5]

                timeForAnalysis = datetime.strptime(str(timeForAnalysis), "%H:%M:%S").__format__("%H:%M:%S")
                print(timeForAnalysis)

                actualTime = datetime.now().__format__("%H:%M:%S")
                print(actualTime)

                timeForAnalysis = time.strptime(timeForAnalysis, "%H:%M:%S")
                actualTime = time.strptime(actualTime, "%H:%M:%S")

                print(timeForAnalysis)
                print(actualTime)

                sleep = time.mktime(timeForAnalysis) - time.mktime(actualTime)
                print(sleep)

            cur.close()
            conn.close()

            if resultSet is not None:
                if sleep > 0:
                    time.sleep(sleep)
                print('SE EJECUTARIA EL ANALYZER')
                command = 'python3 /root/PycharmProjects/TFM/analyzer/main.py {} \'{}\' \'{}\' {} {}'.format(port, ip, organization, domain, tecnologia)
                proc = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
                (out, err) = proc.communicate()
                print(out)
            else:
                time.sleep(sleep)
        except Exception as ex:
            print('ERROR {0}'.format(ex))
            break
        finally:
            if conn is not None:
                conn.close()
