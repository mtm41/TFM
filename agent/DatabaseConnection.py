import sqlite3
from sqlite3 import Error


class DatabaseConnection:
    conn = None
    dbFile = 'D://diagnose.sqlite'

    def __init__(self, dba_file):
        try:
            self.conn = sqlite3.connect(dba_file)
            print(sqlite3.version)
            self.check()
        except:
            print('Error. No se ha podido conectar con la base de datos.')

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
                        formato text
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
                        descripcion text NOT NULL,
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
                        eventID integer PRIMARY KEY,
                        fecha text NOT NULL,
                        origen text NOT NULL,
                        detalles text NOT NULL,
                        tipo text NOT NULL,
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
            print(e)

    def close(self):
        self.conn.close()
