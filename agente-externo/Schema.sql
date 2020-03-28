CREATE DATABASE IF NOT EXISTS Analysis;
USE Analysis;
CREATE TABLE IF NOT EXISTS Organizacion(
    nombre varchar(20) PRIMARY KEY,
    telefono integer(9) NOT NULL,
    descripcion varchar(50),
    horaAnalisis time NOT NULL,
    email varchar(30) NOT NULL,
    inicioJornada time,
    finJornada time,
    apiKey varchar(20) UNIQUE
);
CREATE TABLE IF NOT EXISTS Servicio(
    ip varchar(15),
    puerto integer(5),
    tecnologia varchar(15) NOT NULL,
    horaAnalisis time,
    organizacion varchar(20),
    domainName varchar(20),
    CONSTRAINT pk_Servicio PRIMARY KEY (ip, puerto, organizacion),
    CONSTRAINT fk_Servicio_Organizacion FOREIGN KEY (organizacion) REFERENCES Organizacion(nombre)
    ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS Prueba(
    ID integer auto_increment PRIMARY KEY,
    nombre varchar(15) NOT NULL,
    tipo varchar(20) NOT NULL,
    fechaInicio datetime NOT NULL,
    fechaFin datetime NOT NULL,
    estado integer(1) NOT NULL,
    descripcion varchar(20),
    consejo varchar(20),
    servicioIP varchar(15) NOT NULL,
    servicioPuerto integer(5) NOT NULL,
    organizacion varchar(20) NOT NULL,
    CONSTRAINT fk_Prueba_Servicio FOREIGN KEY (servicioIP, servicioPuerto, organizacion) REFERENCES Servicio(ip,puerto,organizacion)
    ON DELETE CASCADE
);