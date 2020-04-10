import sqlite3
from sqlite3 import Error


class DatabaseConnection:
    conn = None

    def __init__(self, doCheck=True):
        dbFile = 'D://diagnose.sqlite'
        try:
            self.conn = sqlite3.connect(dbFile)
            print(sqlite3.version)
        except Error as e:
            print(e)
        if doCheck:
            self.check()


    def check(self):
        """ create a database connection to a SQLite database """
        try:
            sql_commands = [
                """ CREATE TABLE IF NOT EXISTS Administrador (
                        email text PRIMARY KEY,
                        analisisExterno integer NOT NULL,
                        generarInforme integer NOT NULL
                ); """,
                """ CREATE TABLE IF NOT EXISTS Informe (
                        numero integer PRIMARY KEY,
                        fecha text UNIQUE,
                        formato text,
                        contenido
                ); """,
                """ CREATE TABLE IF NOT EXISTS Servicio (
                        IP text,
                        puerto integer,
                        fecha text,
                        admin text,
                        PRIMARY KEY (IP,puerto),
                        FOREIGN KEY (admin) REFERENCES Administrador
                ); """,
                """ CREATE TABLE IF NOT EXISTS Prueba (
                        ID integer PRIMARY KEY,
                        nombre text UNIQUE,
                        tipo text NOT NULL,
                        fechaInicio text NOT NULL,
                        fechaFin text NOT NULL,
                        estado text NOT NULL,
                        descripcion text,
                        consejo text,
                        servicioIP text,
                        servicioPuerto integer,
                        FOREIGN KEY (servicioIP, servicioPuerto) REFERENCES Servicio
                ); """,
                """ CREATE TABLE IF NOT EXISTS Accion (
                        nombre text PRIMARY KEY,
                        descripcion text NOT NULL
                ); """,
                """ CREATE TABLE IF NOT EXISTS Incidente (
                        nombre text PRIMARY KEY,
                        descripcion text,
                        criticidad integer,
                        aviso integer NOT NULL,
                        accion text,
                        FOREIGN KEY (accion) REFERENCES Accion
                ); """,
                """ CREATE TABLE IF NOT EXISTS Informe_Incidente (
                        numero integer,
                        nombre text,
                        PRIMARY KEY (numero,nombre),
                        FOREIGN KEY (numero) REFERENCES Informe,
                        FOREIGN KEY (nombre) REFERENCES Incidente
                ); """,
                """ CREATE TABLE IF NOT EXISTS Informe_Servicio (
                        numero integer,
                        servicioIP text,
                        servicioPuerto integer,
                        PRIMARY KEY (numero, servicioIP, servicioPuerto),
                        FOREIGN KEY (numero) REFERENCES Informe,
                        FOREIGN KEY (servicioIP,servicioPuerto) REFERENCES Servicio
                ); """,
                """ CREATE TABLE IF NOT EXISTS Registro (
                        ID integer PRIMARY KEY,
                        fecha text NOT NULL,
                        estado text,
                        descripcion text,
                        incidente text,
                        FOREIGN KEY (incidente) REFERENCES Incidente
                ); """,
                """ CREATE TABLE IF NOT EXISTS Evento (
                        fecha text NOT NULL,
                        origen text NOT NULL,
                        detalles text NOT NULL,
                        usuario text NOT NULL,
                        incidente text NOT NULL,
                        FOREIGN KEY (incidente) REFERENCES Incidente
                ); """,
                """ CREATE TABLE IF NOT EXISTS DgaDomain (
                        ip text PRIMARY KEY,
                        dominio text,
                        dga integer NOT NULL,
                        fecha text NOT NULL
                );"""
            ]
            for sql_command in sql_commands:
                self.conn.execute(sql_command)
        except Error as e:
            print('PETA')
            print(e.__cause__)

        incidents = [
            ('ExternalDeviceConnection', 'Se han hallado evidencias que indican que un dispositivo externo ha sido conectado al equipo en los últimos minutos',
           9, 0, ''),
            ('NewInstallationDetection', 'Se han hallado evidencias que indican que se ha producido instalaciones en el registro de Windows',
             5, 0, ''),
            ('NewInstallation',
             'Se han hallado indicios de que se ha realizado con éxito la instalación de software externo en el sistema',
             5, 0,
             ''),
            ('NewInstallationFromKnownEditor',
             'Se han hallado evidencias de que se ha producido una instalación de software procedente de un editor desconocido en el sistema con éxito',
             6, 0, ''),
            ('NewInstallationFromOwnInstaller',
             'Se han hallado evidencias de que se ha instalado software de un editor desconocido con éxito', 6, 0, ''),
            ('NewInstallationFromOwnEditor',
             'Se han hallado evidencias de que software de un editor desconocido, ha sido instalado mediante un instalador desconocido con éxito en el sistema',
             7, 0, ''),
            ('AntivirusNotInstalled', '', 9, 0, ''),
            ('AntivirusInstalledWithoutVersion',
             'Se ha encontrado un antivirus instalado, pero no se ha podido obtener su version actual',
             4, 0, ''),
            ('AntivirusNotPresent', '', 9, 0, ''),
            ('AntivirusNotUpToDate', '', 7, 0, ''),
            ('UpdateFailed', '', 6, 0, ''),
            ('UpdatesNotEnabled', '', 8, 0, ''),
            ('LastUpdate', '', 1, 0, ''),
            ('FirewallNotEnabled', '', 9, 0, ''),
            ('FirewallDisabledByUser', '', 9, 0, ''),
            ('DgaConnection', '', 10, 0, '')
        ]

        sql = '''INSERT INTO incidente (nombre,descripcion,criticidad,aviso,accion) VALUES (?,?,?,?,?)'''

        self.insert_values(incidents, sql)

    def insert_values(self, events, sql):
        success = True
        try:
            cur = self.conn.cursor()
            for event in events:
                cur.execute(sql, event)
                self.conn.commit()
        except Exception as ex:
            success = False
            print(ex)

        return success

    def close(self):
        self.conn.close()
