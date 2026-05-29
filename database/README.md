# Scripts SQL para MySQL Workbench

## Orden de ejecución

1. `schema.sql` — crea la base `sanitapp`, tablas, restricciones y vista `v_registros_formato`.
2. `seed.sql` — catálogos, equipos y usuarios de prueba.

## Diagrama lógico

```
usuarios ──┬──< registros_limpieza >── areas
           │         │    │    │
           │         │    │    └── frecuencias
           │         │    └── equipos_superficies ── areas
           └──< auditoria_registros
```

## Regla de negocio

Si `estado_cumplimiento = 'no_cumple'`, la **medida correctiva** es obligatoria (CHECK en MySQL).
