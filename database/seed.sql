-- =============================================================================
-- Datos iniciales - ejecutar después de schema.sql
-- Contraseña inicial de superadmin: Cambiar123!
-- (generar nuevo hash con: python scripts/generar_password.py)
-- =============================================================================

USE sanitapp;

INSERT INTO frecuencias (nombre, descripcion) VALUES
  ('Diaria', 'Actividad cada día'),
  ('Semanal', 'Una vez por semana'),
  ('Quincenal', 'Cada quince días'),
  ('Mensual', 'Una vez al mes'),
  ('Por evento', 'Cuando aplique un evento específico');

INSERT INTO areas (nombre, descripcion) VALUES
  ('Producción', 'Área de producción'),
  ('Almacén', 'Área de almacenamiento'),
  ('Cocina / Comedor', 'Zona de alimentos'),
  ('Baños', 'Sanitarios'),
  ('Oficinas', 'Áreas administrativas');

INSERT INTO equipos_superficies (area_id, nombre) VALUES
  (1, 'Mesas de trabajo'),
  (1, 'Básculas'),
  (2, 'Estanterías'),
  (3, 'Superficies de preparación'),
  (4, 'Lavamanos'),
  (5, 'Escritorios');

-- password_hash de "Cambiar123!" (generado con: python scripts/generar_password.py)
INSERT INTO usuarios (nombre_completo, email, username, password_hash, rol) VALUES
  (
    'Super Administrador',
    'superadmin@sanitapp.local',
    'superadmin',
    'scrypt:32768:8:1$mq0dGS7Ynx6QfSQ6$a5efadcc580c1b45f894c6c3038b137c714372dd3abbe39d79b7afd0bc3edf951755b7bc2cdfdac64b2c1ea2bbccc51fb17a0f12b8780e732fa96708e515c8e5',
    'superadmin'
  ),
  (
    'Administrador',
    'admin@sanitapp.local',
    'admin',
    'scrypt:32768:8:1$mq0dGS7Ynx6QfSQ6$a5efadcc580c1b45f894c6c3038b137c714372dd3abbe39d79b7afd0bc3edf951755b7bc2cdfdac64b2c1ea2bbccc51fb17a0f12b8780e732fa96708e515c8e5',
    'admin'
  ),
  (
    'Usuario Operativo',
    'usuario@sanitapp.local',
    'usuario',
    'scrypt:32768:8:1$mq0dGS7Ynx6QfSQ6$a5efadcc580c1b45f894c6c3038b137c714372dd3abbe39d79b7afd0bc3edf951755b7bc2cdfdac64b2c1ea2bbccc51fb17a0f12b8780e732fa96708e515c8e5',
    'usuario'
  );
