create database
if not exists alberdidb;
use alberdidb;
drop table if exists Auditoria_Pago;
drop table if exists Auditoria_Evento;
drop table if exists Administrador;
drop table if exists Pago;
drop table if exists Evento;
drop table if exists Responsable_Llave;
drop table if exists Cuenta;
drop table if exists Cliente;

create table Cliente(
	dni varchar(20) not null,
    nombre varchar(20) not null,
    apellido varchar(20) not null,
    telefono varchar(15) not null,
    institucion varchar(40) default null,
    
    primary key(dni),
    constraint control_long_dni check (char_length(dni) >= 7)
);

drop table if exists Responsable_Llave;
create table Responsable_Llave(
	id_responsable integer AUTO_INCREMENT not null,
    nombre varchar(20) default null,
    apellido varchar(20) default null,
    
    primary key(id_responsable)
);

create table Evento(
	id_evento integer AUTO_INCREMENT not null, 
    descripcion varchar(100) default null,
    fecha_inicio date not null,
    fecha_fin date not null,
    observaciones varchar(100) default null,
    monto_total decimal(10,2) not null,
    adeuda BOOLEAN default TRUE,
    nro_recibo integer default null,
    dni varchar(20) not null,
    id_responsable_apertura integer default null, 
    id_responsable_cierre integer default null,
    
    primary key(id_evento),
    
    constraint fk_cliente foreign key
    (dni) references Cliente(dni),
    
    constraint fk_resp_a foreign key
    (id_responsable_apertura) references 
    Responsable_Llave(id_responsable),
    
    constraint fk_resp_c foreign key
    (id_responsable_cierre) references 
    Responsable_Llave(id_responsable)
    
);

create table Pago(
	id_pago integer AUTO_INCREMENT not null,
    id_evento integer not null,
    monto_pago decimal(10,2) not null,
    fecha date not null,
    
    primary key(id_pago, id_evento),
    
    constraint fk_evento foreign key
    (id_evento) references Evento(id_evento)
);

create table Cuenta(
	nombre_usuario varchar(10) not null,
    email varchar(20) not null, 
    nombre varchar(20) not null,
    apellido varchar(20) not null,
    contraseña varchar(20) not null,
    
    primary key(nombre_usuario),
    constraint uq_email unique (email)
);

create table Administrador(
	nombre_usuario varchar(10) not null,
    
    primary key(nombre_usuario),
    constraint fk_nombre_usuario_admi foreign key
    (nombre_usuario) references Cuenta(nombre_usuario)
);

create table Auditoria_Evento(
	id_evento integer not null,
    nombre_usuario varchar(20) not null,
    
    primary key(id_evento, nombre_usuario),
    
    constraint fk_nombre_usuario_aud_evento foreign key
    (nombre_usuario) references Cuenta(nombre_usuario),
    constraint fk_id_evento foreign key
    (id_evento) references Evento(id_evento)
    
);

create table Auditoria_Pago(
	id_pago integer not null,
    nombre_usuario varchar(20) not null,
    
    primary key(id_pago, nombre_usuario),
    
    constraint fk_nombre_usuario_aud_pago foreign key
    (nombre_usuario) references Cuenta(nombre_usuario),
    constraint fk_id_pago foreign key
    (id_pago) references Pago(id_pago)
    
);
