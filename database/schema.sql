-- =============================================================================
-- SanitApp - Limpieza y desinfección
-- Ejecutar en MySQL Workbench (MySQL 8.0+)
-- =============================================================================

CREATE DATABASE IF NOT EXISTS sanitapp
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE sanitapp;

-- -----------------------------------------------------------------------------
-- Catálogos
-- -----------------------------------------------------------------------------

CREATE TABLE areas (
  id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nombre        VARCHAR(120) NOT NULL,
  descripcion   VARCHAR(255) NULL,
  activo        TINYINT(1) NOT NULL DEFAULT 1,
  creado_en     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_areas_nombre (nombre)
) ENGINE=InnoDB;

CREATE TABLE frecuencias (
  id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nombre        VARCHAR(60) NOT NULL,
  descripcion   VARCHAR(255) NULL,
  activo        TINYINT(1) NOT NULL DEFAULT 1,
  creado_en     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_frecuencias_nombre (nombre)
) ENGINE=InnoDB;

CREATE TABLE equipos_superficies (
  id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  area_id       INT UNSIGNED NOT NULL,
  nombre        VARCHAR(150) NOT NULL,
  descripcion   VARCHAR(255) NULL,
  activo        TINYINT(1) NOT NULL DEFAULT 1,
  creado_en     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_equipos_area
    FOREIGN KEY (area_id) REFERENCES areas (id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  UNIQUE KEY uk_equipo_area (area_id, nombre)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- Usuarios y roles
-- -----------------------------------------------------------------------------

CREATE TABLE usuarios (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nombre_completo VARCHAR(150) NOT NULL,
  email           VARCHAR(150) NOT NULL,
  username        VARCHAR(60) NOT NULL,
  password_hash   VARCHAR(255) NOT NULL,
  rol             ENUM('superadmin', 'admin', 'usuario') NOT NULL DEFAULT 'usuario',
  activo          TINYINT(1) NOT NULL DEFAULT 1,
  ultimo_acceso   DATETIME NULL,
  creado_en       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_usuarios_email (email),
  UNIQUE KEY uk_usuarios_username (username),
  INDEX idx_usuarios_rol (rol),
  INDEX idx_usuarios_activo (activo)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- Registro diario de limpieza y desinfección
-- -----------------------------------------------------------------------------

CREATE TABLE registros_limpieza (
  id                  INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  fecha               DATE NOT NULL,
  area_id             INT UNSIGNED NOT NULL,
  equipo_superficie_id INT UNSIGNED NOT NULL,
  frecuencia_id       INT UNSIGNED NOT NULL,
  estado_cumplimiento ENUM('cumple', 'no_cumple') NOT NULL,
  medida_correctiva   TEXT NULL,
  responsable_id      INT UNSIGNED NOT NULL,
  registrado_por_id   INT UNSIGNED NOT NULL,
  observaciones       VARCHAR(500) NULL,
  creado_en           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_registro_area
    FOREIGN KEY (area_id) REFERENCES areas (id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_registro_equipo
    FOREIGN KEY (equipo_superficie_id) REFERENCES equipos_superficies (id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_registro_frecuencia
    FOREIGN KEY (frecuencia_id) REFERENCES frecuencias (id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_registro_responsable
    FOREIGN KEY (responsable_id) REFERENCES usuarios (id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_registro_creador
    FOREIGN KEY (registrado_por_id) REFERENCES usuarios (id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT chk_medida_si_no_cumple CHECK (
    estado_cumplimiento = 'cumple'
    OR (estado_cumplimiento = 'no_cumple' AND medida_correctiva IS NOT NULL AND TRIM(medida_correctiva) <> '')
  ),
  INDEX idx_registros_fecha (fecha),
  INDEX idx_registros_area_fecha (area_id, fecha),
  INDEX idx_registros_responsable (responsable_id),
  INDEX idx_registros_estado (estado_cumplimiento)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- Auditoría de cambios en registros
-- -----------------------------------------------------------------------------

CREATE TABLE auditoria_registros (
  id                BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  registro_id       INT UNSIGNED NOT NULL,
  usuario_id        INT UNSIGNED NOT NULL,
  accion            ENUM('crear', 'actualizar', 'eliminar') NOT NULL,
  datos_anteriores  JSON NULL,
  datos_nuevos      JSON NULL,
  creado_en         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_auditoria_registro
    FOREIGN KEY (registro_id) REFERENCES registros_limpieza (id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_auditoria_usuario
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  INDEX idx_auditoria_registro (registro_id),
  INDEX idx_auditoria_fecha (creado_en)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- Vista para consulta del formato (reporte diario)
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW v_registros_formato AS
SELECT
  r.id,
  r.fecha AS FECHA,
  a.nombre AS AREA,
  e.nombre AS EQUIPO_O_SUPERFICIE,
  f.nombre AS FRECUENCIA,
  CASE WHEN r.estado_cumplimiento = 'no_cumple' THEN 'X' ELSE '' END AS NO_CUMPLE,
  CASE WHEN r.estado_cumplimiento = 'cumple' THEN 'X' ELSE '' END AS CUMPLE,
  r.medida_correctiva AS MEDIDA_CORRECTIVA,
  u.nombre_completo AS RESPONSABLE,
  r.observaciones,
  r.creado_en,
  r.actualizado_en
FROM registros_limpieza r
INNER JOIN areas a ON a.id = r.area_id
INNER JOIN equipos_superficies e ON e.id = r.equipo_superficie_id
INNER JOIN frecuencias f ON f.id = r.frecuencia_id
INNER JOIN usuarios u ON u.id = r.responsable_id;
