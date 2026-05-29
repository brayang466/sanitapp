-- Columna avatar para foto de perfil (ejecutar una vez en Workbench)
USE sanitapp;

ALTER TABLE usuarios
  ADD COLUMN avatar VARCHAR(255) NULL AFTER activo;
