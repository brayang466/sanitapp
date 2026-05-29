-- Actualizar cuenta administrador — ejecutar en MySQL Workbench
-- (Compatible con "Safe Updates" de Workbench)
USE sanitapp;

-- Ejecutar antes si no tiene columna avatar: database/agregar_avatar_usuarios.sql

-- Opción 1: si el usuario sigue siendo "admin"
UPDATE usuarios SET
  nombre_completo = 'Paula Isidro',
  email = 'coordinacion.lyd@colbeef.com',
  username = 'paula.isidro',
  password_hash = 'scrypt:32768:8:1$eKruz2yACM0cHgie$94b4dcdae31bce52f7370bbea16cd23cd4147eda65500a2a6fb156aa0593bea0c072f1dcf5668d735a055131f5ff28dc76bc6809374ee2176f1d75415de3f291',
  activo = 1
WHERE username = 'admin';

-- Si la opción 1 actualizó 0 filas, ejecute solo esta línea (ya estaba como paula.isidro):
-- UPDATE usuarios SET nombre_completo = 'Paula Isidro', email = 'coordinacion.lyd@colbeef.com',
--   password_hash = 'scrypt:32768:8:1$eKruz2yACM0cHgie$94b4dcdae31bce52f7370bbea16cd23cd4147eda65500a2a6fb156aa0593bea0c072f1dcf5668d735a055131f5ff28dc76bc6809374ee2176f1d75415de3f291', activo = 1
-- WHERE username = 'paula.isidro';

SELECT id, nombre_completo, username, email, rol, activo
FROM usuarios
WHERE username = 'paula.isidro';
