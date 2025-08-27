create database if not exists alberdidb;
use alberdidb;

drop table if exists auditoria_pago;
drop table if exists auditoria_evento;
drop table if exists administrador;
drop table if exists pago;
drop table if exists evento;
drop table if exists responsable_llave;
drop table if exists cuenta;
drop table if exists cliente;

create table cliente(
    dni varchar(20) not null,
    nombre varchar(20) not null,
    apellido varchar(20) not null,
    telefono varchar(15) not null,
    institucion varchar(40) default null,
    primary key(dni),
    constraint control_long_dni check (char_length(dni) >= 7)
);

create table responsable_llave(
    id_responsable integer auto_increment not null,
    nombre varchar(20) default null,
    apellido varchar(20) default null,
    primary key(id_responsable)
);


create table cuenta(
    nombre_usuario varchar(10) not null,
    email varchar(50) not null,
    nombre varchar(20) not null,
    apellido varchar(20) not null,
    contraseña varchar(255) not null,
    primary key(nombre_usuario),
    constraint uq_email unique (email)
);


create table evento(
    id_evento integer auto_increment not null,
    descripcion varchar(100) default null,
    fecha_inicio date not null,
    fecha_fin date not null,
    observaciones varchar(100) default null,
    monto_total decimal(10,2) not null,
    adeuda boolean default true,
    nro_recibo integer default null,
    dni varchar(20) not null,
    id_responsable_apertura integer default null,
    id_responsable_cierre integer default null,
    usuario_creacion varchar(10) not null,
    primary key(id_evento),
    constraint fk_cliente foreign key (dni) references cliente(dni),
    constraint fk_resp_a foreign key (id_responsable_apertura) references responsable_llave(id_responsable),
    constraint fk_resp_c foreign key (id_responsable_cierre) references responsable_llave(id_responsable),
    constraint fk_usuario_evento foreign key (usuario_creacion) references cuenta(nombre_usuario)
);

create table pago(
    id_pago integer auto_increment not null,
    id_evento integer not null,
    monto_pago decimal(10,2) not null,
    fecha date not null,
    usuario_creacion varchar(10) not null,
    primary key(id_pago),
    constraint fk_evento foreign key (id_evento) references evento(id_evento),
    constraint fk_usuario_pago foreign key (usuario_creacion) references cuenta(nombre_usuario)
);


create table administrador(
    nombre_usuario varchar(10) not null,
    primary key(nombre_usuario),
    constraint fk_nombre_usuario_admi foreign key (nombre_usuario) references cuenta(nombre_usuario)
);


create table auditoria_evento(
    id_evento integer not null,
    nombre_usuario varchar(10) not null,
    fecha_auditoria timestamp default current_timestamp,
    primary key(id_evento, nombre_usuario),
    constraint fk_nombre_usuario_aud_evento foreign key (nombre_usuario) references cuenta(nombre_usuario),
    constraint fk_id_evento foreign key (id_evento) references evento(id_evento)
);


create table auditoria_pago(
    id_pago integer not null,
    nombre_usuario varchar(10) not null,
    fecha_auditoria timestamp default current_timestamp,
    primary key(id_pago, nombre_usuario),
    constraint fk_nombre_usuario_aud_pago foreign key (nombre_usuario) references cuenta(nombre_usuario),
    constraint fk_id_pago foreign key (id_pago) references pago(id_pago)
);


delimiter //

create trigger insertar_evento
after insert on evento
for each row
begin
    insert into auditoria_evento (id_evento, nombre_usuario)
    values (new.id_evento, new.usuario_creacion);
end //

create trigger insertar_pago
after insert on pago
for each row
begin
    insert into auditoria_pago(id_pago, nombre_usuario)
    values (new.id_pago, new.usuario_creacion);
end //

delimiter ;