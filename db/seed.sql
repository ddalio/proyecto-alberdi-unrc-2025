-- Usar la base de datos
USE alberdidb;

-- Limpiar datos previos (para evitar errores de claves duplicadas)
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE auditoria_pago;
TRUNCATE TABLE auditoria_evento;
TRUNCATE TABLE administrador;
TRUNCATE TABLE pago;
TRUNCATE TABLE evento;
TRUNCATE TABLE responsable_llave;
TRUNCATE TABLE cuenta;
TRUNCATE TABLE cliente;
SET FOREIGN_KEY_CHECKS = 1;

-- ==============================
-- 1. CLIENTES
-- ==============================
INSERT INTO cliente (dni, nombre, apellido, telefono, institucion) VALUES
('12345678', 'Pepe', 'Garcia', '3512345678', 'UNRC'),
('23456789', 'Ana', 'Lopez', '3519876543', 'Colegio Alberdi'),
('34567890', 'Juan', 'Perez', '3581112233', NULL);

-- ==============================
-- 2. RESPONSABLES DE LLAVE
-- ==============================
INSERT INTO responsable_llave (nombre, apellido) VALUES
('Carlos', 'Diaz'),
('Laura', 'Martinez');

-- ==============================
-- 3. CUENTAS DE USUARIOS
-- ==============================
INSERT INTO cuenta (nombre_usuario, email, nombre, apellido, contrasenia) VALUES
('admin01', 'admin01@example.com', 'Mario', 'Suarez', 'pass123'),
('user01', 'user01@example.com', 'Lucia', 'Fernandez', 'pass456'),
('user02', 'user02@example.com', 'Pablo', 'Gomez', 'pass789');

-- ==============================
-- 4. EVENTOS
-- ==============================
-- NOTA: 
-- - dni debe existir en cliente
-- - id_responsable_apertura y cierre deben existir en responsable_llave
-- - usuario_creacion debe existir en cuenta
INSERT INTO evento (descripcion, fecha_inicio, fecha_fin, observaciones, monto_total, adeuda, nro_recibo, dni, id_responsable_apertura, id_responsable_cierre, usuario_creacion) VALUES
('Fiesta de graduación', '2025-09-10', '2025-09-10', 'Evento anual de egresados', 150000.00, TRUE, NULL, '12345678', 1, NULL, 'user01'),
('Reunión institucional', '2025-09-15', '2025-09-15', 'Reunión mensual de directivos', 50000.00, TRUE, NULL, '23456789', 2, NULL, 'user01'),
('Conferencia educativa', '2025-09-20', '2025-09-20', NULL, 80000.00, TRUE, NULL, '34567890', 1, NULL, 'user02');

-- ==============================
-- 5. PAGOS
-- ==============================
-- NOTA:
-- - id_evento debe existir en evento
-- - usuario_creacion debe existir en cuenta
INSERT INTO pago (id_evento, monto_pago, fecha, usuario_creacion) VALUES
(1, 75000.00, '2025-09-05', 'user02'),
(1, 75000.00, '2025-09-06', 'user02'),
(2, 50000.00, '2025-09-07', 'user01');

-- ==============================
-- 6. ADMINISTRADORES
-- ==============================
-- NOTA: nombre_usuario debe existir en cuenta
INSERT INTO administrador (nombre_usuario) VALUES
('admin01');
