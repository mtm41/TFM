USE Analysis;
CREATE TABLE IF NOT EXISTS Organizacion(
    nombre varchar(20) PRIMARY KEY,
    telefono integer(9) NOT NULL,
    descripcion varchar(50),
    horaAnalisis time NOT NULL,
    email varchar(30) NOT NULL
);
CREATE TABLE IF NOT EXISTS Servicio(
    ip varchar(15),
    puerto integer(5),
    tecnologia varchar(15) NOT NULL,
    horaAnalisis time,
    organizacion varchar(20) NOT NULL,
    CONSTRAINT pk_Servicio PRIMARY KEY (ip, puerto),
    CONSTRAINT fk_Servicio_Organizacion FOREIGN KEY (organizacion) REFERENCES Organizacion(nombre)
);
CREATE TABLE IF NOT EXISTS Prueba(
    ID integer auto_increment PRIMARY KEY,
    nombre varchar(15) NOT NULL,
    tipo varchar(20) NOT NULL,
    fechaInicio date NOT NULL,
    fechaFin date NOT NULL,
    estado integer(1) NOT NULL,
    descripcion varchar(20),
    consejo varchar(20),
    servicioIP varchar(15) NOT NULL,
    servicioPuerto integer(5) NOT NULL,
    CONSTRAINT fk_Prueba_Servicio FOREIGN KEY (servicioIP, servicioPuerto) REFERENCES Servicio(ip,puerto)
);