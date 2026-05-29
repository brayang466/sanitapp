-- =============================================================================
-- SanitApp - INSTALACIÓN COMPLETA (MySQL Workbench 8.0+)
-- =============================================================================
-- INSTRUCCIONES:
--   1. Busca abajo la línea: SET @password_admin = '...';
--   2. Sustituye por TU contraseña personalizada (ej: 'SanitApp2026#')
--   3. Ejecuta TODO el script con root en Workbench (Ctrl+Shift+Enter)
--
-- Resultado:
--   - Base de datos: sanitapp
--   - Usuario MySQL: admin  (con todos los permisos sobre sanitapp)
--   - Tabla del formato con: FECHA, AREA, EQUIPO_O_SUPERFICIE, FRECUENCIA,
--     NO_CUMPLE, CUMPLE, MEDIDA_CORRECTIVA, RESPONSABLE
--   - Tabla usuarios de la app: superadmin, admin, usuario
-- =============================================================================

-- >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
-- CAMBIA SOLO ESTA LÍNEA POR TU CONTRASEÑA
SET @password_admin = 'Adm2026**';
-- <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

-- -----------------------------------------------------------------------------
-- 1. Base de datos
-- -----------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS sanitapp
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 2. Usuario MySQL "admin" con todos los permisos sobre sanitapp
-- -----------------------------------------------------------------------------
DROP USER IF EXISTS 'admin'@'localhost';
DROP USER IF EXISTS 'admin'@'127.0.0.1';

SET @sql_crear_admin = CONCAT(
  "CREATE USER 'admin'@'localhost' IDENTIFIED BY '",
  REPLACE(@password_admin, "'", "''"),
  "'"
);
PREPARE stmt_admin FROM @sql_crear_admin;
EXECUTE stmt_admin;
DEALLOCATE PREPARE stmt_admin;

SET @sql_crear_admin_ip = CONCAT(
  "CREATE USER 'admin'@'127.0.0.1' IDENTIFIED BY '",
  REPLACE(@password_admin, "'", "''"),
  "'"
);
PREPARE stmt_admin_ip FROM @sql_crear_admin_ip;
EXECUTE stmt_admin_ip;
DEALLOCATE PREPARE stmt_admin_ip;

GRANT ALL PRIVILEGES ON sanitapp.* TO 'admin'@'localhost';
GRANT ALL PRIVILEGES ON sanitapp.* TO 'admin'@'127.0.0.1';

FLUSH PRIVILEGES;

-- -----------------------------------------------------------------------------
-- 3. Tablas (conectar como admin o seguir con root)
-- -----------------------------------------------------------------------------
USE sanitapp;

-- Usuarios de la aplicación (login web)
DROP TABLE IF EXISTS auditoria_registros;
DROP TABLE IF EXISTS responsables;
DROP TABLE IF EXISTS registros_formato;
DROP TABLE IF EXISTS registros_limpieza;
DROP TABLE IF EXISTS equipos_superficies;
DROP TABLE IF EXISTS areas;
DROP TABLE IF EXISTS frecuencias;
DROP TABLE IF EXISTS usuarios;

CREATE TABLE usuarios (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nombre_completo VARCHAR(150) NOT NULL,
  email           VARCHAR(150) NOT NULL,
  username        VARCHAR(60) NOT NULL,
  password_hash   VARCHAR(255) NOT NULL,
  rol             ENUM('superadmin', 'admin', 'usuario') NOT NULL DEFAULT 'usuario',
  activo          TINYINT(1) NOT NULL DEFAULT 1,
  avatar          VARCHAR(255) NULL,
  ultimo_acceso   DATETIME NULL,
  creado_en       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_usuarios_email (email),
  UNIQUE KEY uk_usuarios_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Personal responsable de los registros (lista seleccionable)
CREATE TABLE responsables (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nombre_completo VARCHAR(150) NOT NULL,
  activo          TINYINT(1) NOT NULL DEFAULT 1,
  creado_en       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_responsables_nombre (nombre_completo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla principal = campos del formato de limpieza y desinfección
CREATE TABLE registros_formato (
  id                    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  FECHA                 DATE NOT NULL,
  AREA                  VARCHAR(120) NOT NULL,
  EQUIPO_O_SUPERFICIE   VARCHAR(150) NOT NULL,
  FRECUENCIA            VARCHAR(60) NOT NULL,
  NO_CUMPLE             TINYINT(1) NOT NULL DEFAULT 0 COMMENT '1 = marcado',
  CUMPLE                TINYINT(1) NOT NULL DEFAULT 0 COMMENT '1 = marcado',
  MEDIDA_CORRECTIVA     TEXT NULL,
  RESPONSABLE           VARCHAR(150) NOT NULL,
  creado_por_id         INT UNSIGNED NULL,
  creado_en             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_registro_creado_por
    FOREIGN KEY (creado_por_id) REFERENCES usuarios (id)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT chk_solo_un_cumplimiento CHECK (
    (NO_CUMPLE = 1 AND CUMPLE = 0) OR (NO_CUMPLE = 0 AND CUMPLE = 1)
  ),
  CONSTRAINT chk_medida_si_no_cumple CHECK (
    NO_CUMPLE = 0
    OR (
      NO_CUMPLE = 1
      AND MEDIDA_CORRECTIVA IS NOT NULL
      AND TRIM(MEDIDA_CORRECTIVA) <> ''
    )
  ),
  INDEX idx_fecha (FECHA),
  INDEX idx_area (AREA),
  INDEX idx_responsable (RESPONSABLE)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Vista con los mismos nombres del papel (para reportes en Workbench)
CREATE OR REPLACE VIEW v_formato_diario AS
SELECT
  id,
  FECHA,
  AREA,
  EQUIPO_O_SUPERFICIE,
  FRECUENCIA,
  CASE WHEN NO_CUMPLE = 1 THEN 'X' ELSE '' END AS `NO CUMPLE`,
  CASE WHEN CUMPLE = 1 THEN 'X' ELSE '' END AS CUMPLE,
  MEDIDA_CORRECTIVA,
  RESPONSABLE,
  creado_en,
  actualizado_en
FROM registros_formato;

-- -----------------------------------------------------------------------------
-- 4. Usuarios iniciales de la aplicación (contraseña: Cambiar123!)
-- -----------------------------------------------------------------------------
INSERT INTO usuarios (nombre_completo, email, username, password_hash, rol) VALUES
(
  'Super Administrador',
  'superadmin@sanitapp.local',
  'superadmin',
  'scrypt:32768:8:1$mq0dGS7Ynx6QfSQ6$a5efadcc580c1b45f894c6c3038b137c714372dd3abbe39d79b7afd0bc3edf951755b7bc2cdfdac64b2c1ea2bbccc51fb17a0f12b8780e732fa96708e515c8e5',
  'superadmin'
),
(
  'Paula Isidro',
  'coordinacion.lyd@colbeef.com',
  'paula.isidro',
  'scrypt:32768:8:1$eKruz2yACM0cHgie$94b4dcdae31bce52f7370bbea16cd23cd4147eda65500a2a6fb156aa0593bea0c072f1dcf5668d735a055131f5ff28dc76bc6809374ee2176f1d75415de3f291',
  'admin'
),
(
  'Usuario común',
  'usuario@sanitapp.local',
  'usuario',
  'scrypt:32768:8:1$mq0dGS7Ynx6QfSQ6$a5efadcc580c1b45f894c6c3038b137c714372dd3abbe39d79b7afd0bc3edf951755b7bc2cdfdac64b2c1ea2bbccc51fb17a0f12b8780e732fa96708e515c8e5',
  'usuario'
);

-- -----------------------------------------------------------------------------
-- 5. Responsables (personal)
-- -----------------------------------------------------------------------------
INSERT INTO responsables (nombre_completo) VALUES
('PEDRO ARMANDO PEÑA ARENAS'),
('JHON FREDY MORALES ARIAS'),
('LEONARDO CORREA MANRIQUE'),
('ALEXIS DARIO BARRAZA GARCIA'),
('ALEXANDER JIMENEZ RODRIGUEZ'),
('HELVER JOSE FLOREZ PEDROZO'),
('HENRY ARMANDO LOPEZ PINTO'),
('EDWARD ALEXANDER ARDILA SALAS'),
('LUIS HERNANDO LOBO VELASQUEZ'),
('CARLOS ALFREDO GONZALEZ DIAZ'),
('ANDREY ALIRIO PARADA SILVA'),
('JORGE ELIECER TORRES'),
('MANZUR NAIN MANZANO LIZARAZO'),
('LUDDALLAMON PINTO RANGEL'),
('JOSE MIGUEL MARMOL CAPATAZ'),
('JOSE DANIEL BAUTISTA CRUZ'),
('DUBIAN ERNEY RINCON MENDOZA'),
('JOHN EDWIN BLANCO CAVIEDES'),
('CRISTHIAN OMAR QUINTERO REYES'),
('ANDRES FELIPE BOHORQUEZ ANGARITA'),
('MATHA JANETH JAIMES VARGAS'),
('PEDRO JOSE HERNANDEZ DURAN');

-- -----------------------------------------------------------------------------
-- 6. Ejemplo de registro del día (opcional, puedes borrar estas líneas)
-- -----------------------------------------------------------------------------
INSERT INTO registros_formato (
  FECHA, AREA, EQUIPO_O_SUPERFICIE, FRECUENCIA,
  NO_CUMPLE, CUMPLE, MEDIDA_CORRECTIVA, RESPONSABLE, creado_por_id
) VALUES
(
  CURDATE(),
  'Producción',
  'Mesas de trabajo',
  'Diaria',
  0, 1, NULL,
  'PEDRO ARMANDO PEÑA ARENAS',
  3
);

-- -----------------------------------------------------------------------------
-- 7. Verificación
-- -----------------------------------------------------------------------------
SELECT 'Base de datos creada' AS resultado, DATABASE() AS bd_actual;
SHOW GRANTS FOR 'admin'@'localhost';
SELECT * FROM v_formato_diario;
