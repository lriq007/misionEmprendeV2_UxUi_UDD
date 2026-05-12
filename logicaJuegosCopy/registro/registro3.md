# Registro 3 - Sesion completa integrada

Fecha de registro: 2026-05-09

Este registro documenta la nueva orquestacion completa por terminal agregada en:

```text
cli/ejecutarSesionCompleta.py
```

La CLI integra las cinco etapas existentes en el orden del juego original:

```text
1. Sopa de letras
2. Bubble Map
3. LEGO MVP
4. Creacion del Pitch
5. Negociacion
```

## Comando principal

```bash
python -m cli.ejecutarSesionCompleta
```

Para pruebas rapidas:

```bash
python -m cli.ejecutarSesionCompleta \
  --duracion-sopa 3 \
  --duracion-bubble 3 \
  --duracion-lego 3 \
  --duracion-pitch 3 \
  --duracion-exposicion 1 \
  --tolerancia-oculta 0 \
  --mostrar-ranking 0
```

## Refactor realizado

Cada CLI individual conserva su comando original, pero ahora expone una funcion reutilizable:

```text
cli.ejecutarSesionSopa.ejecutarEtapaSopa(...)
cli.ejecutarSesionBubbleMap.ejecutarEtapaBubbleMap(...)
cli.ejecutarSesionLego.ejecutarEtapaLego(...)
cli.ejecutarSesionPitchCreacion.ejecutarEtapaPitchCreacion(...)
cli.ejecutarSesionNegociacion.ejecutarEtapaNegociacion(...)
```

Los comandos individuales siguen funcionando:

```bash
python -m cli.ejecutarSesionSopa
python -m cli.ejecutarSesionBubbleMap
python -m cli.ejecutarSesionLego
python -m cli.ejecutarSesionPitchCreacion
python -m cli.ejecutarSesionNegociacion
```

La diferencia es que cada funcion acepta opcionalmente una `SesionJuego` compartida. Si no se entrega, la etapa crea su propia sesion como antes.

## Cronometro global real

La sesion completa crea una sola instancia de:

```text
SesionJuego(nombreSesion="Sesion completa logica de juegos")
```

Luego llama una sola vez:

```python
sesion.iniciarSesion()
```

Cada etapa llama:

```python
sesion.iniciarEtapa()
sesion.finalizarEtapa()
```

El cronometro global solo se detiene al final de Negociacion:

```python
sesion.finalizarSesion()
```

Para soportar este flujo se agregaron metodos en `competencia/sesionJuego.py`:

```text
finalizarEtapa()
registrarTiempoGlobal()
```

Esto separa el cierre de una etapa del cierre de toda la sesion.

## Ranking general acumulado

La fuente acumulada sigue siendo:

```text
output/RankingGeneral.csv
```

La sesion completa carga una vez el ranking general con:

```python
rankingGeneral = cargarRankingGeneral(rutaRankingGeneral, rutaSesion)
```

Ese mismo diccionario se pasa a todas las etapas. Cada etapa usa las funciones idempotentes ya existentes:

```text
aplicarRankingGeneralParaSopa / actualizarGeneralConSopa
aplicarRankingGeneralParaBubbleMap / actualizarGeneralConBubbleMap
aplicarRankingGeneralParaLego / actualizarGeneralConLego
aplicarRankingGeneralParaPitchCreacion / actualizarGeneralConPitchCreacion
aplicarRankingGeneralParaNegociacion / actualizarGeneralConNegociacion
```

El mecanismo evita duplicar puntajes porque antes de recalcular una etapa se descuenta su aporte anterior y luego se reemplaza por el nuevo resultado.

Al terminar cada etapa se imprime el ranking parcial destacando a:

```text
Equipo Usuario
```

Al terminar toda la sesion se imprime el ranking final y se exporta nuevamente:

```text
output/RankingGeneral.csv
```

## Migracion sugerida a Django

La orquestacion de `ejecutarSesionCompleta.py` puede migrarse a Django separando responsabilidades:

```text
models.py
  Team
  GameSession
  StageRun
  StageScore
  PitchSubmission
  LegoSubmission
  NegotiationEvaluation

services/session_flow.py
  iniciar_sesion_completa()
  iniciar_etapa(session, tipo_etapa)
  cerrar_etapa(session, tipo_etapa)
  cerrar_sesion(session)

services/scoring.py
  recalcular_sopa(team, entregable)
  recalcular_bubble_map(team, respuestas)
  recalcular_lego(team, entrega)
  recalcular_pitch(team, guion)
  recalcular_negociacion(team, evaluaciones)
```

La regla importante para Django es mantener la misma idea de idempotencia:

```text
No sumar tokens a ciegas.
Guardar el aporte por etapa.
Recalcular y reemplazar el aporte de esa etapa cuando cambie el entregable.
Actualizar tokensTotales desde los aportes guardados.
```

El cronometro global debe vivir en `GameSession`:

```text
started_at
finished_at
```

Cada etapa debe vivir en `StageRun`:

```text
stage_type
started_at
finished_at
duration_seconds
```

En vistas Django, el flujo equivalente seria:

```text
/sesion/iniciar/
/sesion/<id>/sopa/
/sesion/<id>/bubble-map/
/sesion/<id>/lego/
/sesion/<id>/pitch/
/sesion/<id>/negociacion/
/sesion/<id>/ranking-final/
```

El ranking final debe consultarse desde base de datos ordenando por `tokens_totales`, usando desempates equivalentes a `puntajes/ranking.py`.

## Verificacion

Se ejecuto:

```bash
logiJuegos/bin/python -m compileall competencia juegos puntajes espera cli
```

Resultado: compilacion correcta de los paquetes modificados.
