# Logica Juegos

Proyecto de logica pura para probar mini juegos por terminal antes de migrarlos a Django.

## Ejecutar demo

```bash
source logiJuegos/bin/activate
python -m cli.ejecutarSesionSopa
```

Para pruebas rapidas:

```bash
python -m cli.ejecutarSesionSopa --duracion 10
```

## Flujo actual

- Inicia cronometro global de sesion.
- Inicia cronometro particular de etapa.
- Ejecuta sopa de letras con 8 palabras.
- Si el equipo termina antes del cierre, habilita buscaminas de espera.
- Al cerrar la etapa, calcula tokens de sopa y bonus.
- Genera `output/Ranking.csv` con posicion, tokens finales y tiempos.

## Equivalencia con Django

- `SesionJuego` representa conceptualmente a `GameSession`.
- `Equipo` representa conceptualmente a `Team`.
- El estado de sopa representa conceptualmente a `TeamGameSession`.
- `tokensEmpatia`, `tokensCreatividad`, `tokensEvaluacion` y `tokensTotales` reflejan los campos actuales de `Team`.
