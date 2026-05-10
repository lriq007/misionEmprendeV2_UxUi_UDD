# Registro 2 - Estado actualizado del sistema de logica de juegos

Fecha de registro: 2026-05-09

Este registro actualiza `registro1.md`. Describe el estado actual del proyecto `logicaJuegos` despues de incorporar la etapa Bubble Map, manteniendo la sopa de letras, el buscaminas de espera, cronometros, ranking y exportacion CSV.

El objetivo del documento es permitir reconstruir esta version del sistema o entregar contexto tecnico a otra IA para migrar la logica al proyecto Django base.

## Objetivo del proyecto

El proyecto implementa mini juegos y actividades por terminal usando Python puro. No levanta servidor. El CLI simula lo que en Django luego se repartiria entre:

```text
models.py
views.py
services/scoring.py
templates
JavaScript
```

La regla arquitectonica principal es:

```text
Los juegos calculan resultados.
Las reglas de puntaje transforman resultados en tokens.
El ranking global se ordena por tokensTotales.
```

Esto replica el modelo real donde el ranking final se basa en:

```text
Team.tokens_totales
```

## Entorno

Entorno virtual:

```bash
logiJuegos
```

Activacion:

```bash
source logiJuegos/bin/activate
```

Version de Python:

```text
Python 3.12.3
```

No hay dependencias externas. Solo se usan librerias estandar.

## Librerias estandar usadas

- `argparse`: argumentos del CLI.
- `csv`: carga de equipos simulados y exportacion de ranking.
- `dataclasses`: modelos simples de datos.
- `pathlib`: rutas.
- `random`: sopa de letras y buscaminas.
- `select`: entrada por terminal con tiempo limite.
- `string`: letras aleatorias.
- `sys`: lectura de `stdin`.
- `time.monotonic`: medicion estable de tiempo.
- `time.sleep`: espera de cierre de etapa y despliegue de ranking.

## Estructura actual

```text
logicaJuegos/
  cli/
    __init__.py
    ejecutarSesionSopa.py
    ejecutarSesionBubbleMap.py
    ejecutarSesionLego.py
    ejecutarSesionPitchCreacion.py
    ejecutarSesionNegociacion.py

  competencia/
    __init__.py
    cronometro.py
    csvRanking.py
    csvBubbleMap.py
    csvLego.py
    csvPitch.py
    csvNegociacion.py
    equipo.py
    rankingGeneral.py
    sesionJuego.py

  data/
    equiposSesion.csv
    equiposSimulados.csv
    equiposSimuladosBubbleMap.csv
    equiposSimuladosLego.csv
    equiposSimuladosPitch.csv
    equiposNegociacion.csv
    evaluacionesNegociacion.csv

  espera/
    __init__.py
    buscaminasEspera.py

  juegos/
    __init__.py
    juegoSopaLetras.py
    mapaEmpatia.py
    creacionPitch.py
    negociacion.py

  output/
    Ranking.csv
    RankingBubbleMap.csv
    RankingLego.csv
    RankingPitchCreacion.csv
    RankingNegociacion.csv
    RankingGeneral.csv

  puntajes/
    __init__.py
    ranking.py
    reglaPuntajeSopaLetras.py
    reglaPuntajeMapaEmpatia.py
    reglaPuntajeLego.py
    reglaPuntajePitch.py
    reglaPuntajeNegociacion.py

  registro/
    registro1.md
    registro2.md

  README.md
  .gitignore
```

## Reglas globales

### Ranking general acumulado

Se agrego un ranking general persistido en CSV:

```text
output/RankingGeneral.csv
```

Este archivo representa el estado acumulado de la sesion simulada. Cada CLI de juego sigue generando su CSV especifico de etapa, pero ademas actualiza el ranking general.

```text
Sopa de letras:
  output/Ranking.csv
  output/RankingGeneral.csv

Bubble Map:
  output/RankingBubbleMap.csv
  output/RankingGeneral.csv
```

El archivo base de equipos de sesion es:

```text
data/equiposSesion.csv
```

El ranking general guarda tokens por categoria y tambien aportes por etapa:

```text
tokensEmpatia
tokensCreatividad
tokensEvaluacion
tokensTotales
tokensSopa
tokensBubbleMap
tokensLego
tokensPitchCreacion
tokensNegociacion
subioImagenLego
imagenLego
mensajesLego
tipoMensajeLego
nombreProductoPitch
finalizoPitchCreacion
tiempoPitchCreacionSegundos
ordenExposicion
promedioEvaluacionRecibida
evaluacionesRecibidas
```

La actualizacion es idempotente por etapa. Esto significa que si una CLI se ejecuta dos veces, el sistema reemplaza el aporte de esa etapa en vez de duplicarlo accidentalmente.

Esta decision es importante para la futura migracion a Django, porque replica mejor el enfoque correcto:

```text
recalcular tokens desde entregables
no sumar tokens a ciegas cada vez que se guarda
```

### Cronometros

Cada sesion usa:

```text
cronometroGlobal
cronometroEtapa
```

El global mide la sesion completa. El de etapa mide el juego o actividad actual.

La clase esta en:

```text
competencia/cronometro.py
```

Usa `time.monotonic()` para evitar errores si cambia el reloj del sistema.

### Control estricto del tiempo

La entrada por terminal usa `select`, por lo que el usuario solo puede responder dentro del tiempo disponible.

Si se acaba el tiempo:

```text
No se aceptan mas entradas.
Se guarda lo que ya fue ingresado.
La etapa se cierra.
```

Regla para Django:

```text
El backend debe rechazar cualquier jugada o respuesta posterior al cierre de la etapa.
```

El frontend puede mostrar temporizador, pero no debe ser la fuente de verdad.

### Buscaminas de espera

El buscaminas es reutilizable para etapas con tiempo.

Archivo:

```text
espera/buscaminasEspera.py
```

Configuracion:

```text
tablero: 4x4
minas: 8
bonus maximo: 1 token
```

Regla global:

```text
Si el equipo finaliza la actividad principal y quedan al menos 5 segundos, se habilita buscaminas.
Si quedan menos de 5 segundos, pasa directo a espera de ranking.
```

El bonus se registra durante la espera y se suma al cierre oficial de la etapa.

### Ranking global

Archivo:

```text
puntajes/ranking.py
```

El ranking global siempre se basa en:

```text
tokensTotales DESC
```

En Bubble Map se usa:

```text
tokensTotales DESC
tiempoGlobalSegundos ASC
tiempoBubbleMapSegundos ASC
nombreEquipo ASC
```

El ranking siempre debe:

```text
- destacar el equipo en sesion;
- mostrar su posicion;
- desplegarse 15 segundos por defecto.
```

En CLI se puede cambiar la duracion de despliegue con:

```bash
--mostrar-ranking
```

## Modelo Equipo

Archivo:

```text
competencia/equipo.py
```

Representa conceptualmente a `Team` del proyecto Django.

Campos principales:

```text
nombreEquipo
tokensEmpatia
tokensCreatividad
tokensEvaluacion
tokensTotales
tiempoGlobalSegundos
bonusEspera
ordenLlegada
```

Campos de sopa:

```text
tiempoSopaSegundos
porcentajeSopa
posicionSopa
```

Campos de Bubble Map:

```text
tiempoBubbleMapSegundos
finalizoBubbleMap
preguntasCompletas
preguntasDetalleIdeal
preguntasDesarrolladas
preguntasSuperficiales
apendicesBasura
apendicesExcesivos
puntajeContenidoBubbleMap
tokensBubbleMap
bonusExcelenciaVelocidad
penalizacionBajaProfundidad
penalizacionCalidadDeficiente
penalizacionExceso
```

Campos de LEGO MVP:

```text
tokensLego
subioImagenLego
imagenLego
mensajesLego
tipoMensajeLego
```

Campos de creacion del pitch:

```text
tokensPitchCreacion
nombreProductoPitch
desafioEmpatiaPitch
creatividadPitch
cierrePitch
finalizoPitchCreacion
tiempoPitchCreacionSegundos
```

Campos de negociacion:

```text
tokensNegociacion
ordenExposicion
promedioEvaluacionRecibida
evaluacionesRecibidas
```

Equivalencia con Django:

```text
Equipo -> Team
tokensEmpatia -> Team.tokens_empatia
tokensCreatividad -> Team.tokens_creatividad
tokensEvaluacion -> Team.tokens_evaluacion
tokensTotales -> Team.tokens_totales
```

## SesionJuego

Archivo:

```text
competencia/sesionJuego.py
```

Representa conceptualmente a `GameSession`.

Responsabilidades:

```text
iniciarSesion()
iniciarEtapa()
finalizarSesion()
segundosRestantesEtapa()
etapaTerminada()
```

## Juego 1 - Sopa de letras

CLI:

```bash
python -m cli.ejecutarSesionSopa
```

Prueba rapida:

```bash
python -m cli.ejecutarSesionSopa --duracion 10
```

Archivos:

```text
cli/ejecutarSesionSopa.py
juegos/juegoSopaLetras.py
puntajes/reglaPuntajeSopaLetras.py
competencia/csvRanking.py
data/equiposSimulados.csv
  output/Ranking.csv
  output/RankingGeneral.csv
```

### Reglas de sopa

- Debe tener minimo 8 palabras y maximo 15.
- El tablero por defecto es 15x15.
- Las palabras se normalizan a mayuscula.
- Se ubican horizontal, vertical y diagonalmente.
- Se rellena el resto con letras aleatorias.

Palabras actuales:

```text
cliente
problema
idea
prototipo
empatia
equipo
pitch
valor
```

### Puntaje de sopa

Ranking interno:

```text
1. Equipos que terminaron, ordenados por menor tiempo.
2. Equipos que no terminaron, ordenados por mayor porcentaje.
3. En empate de porcentaje, se usa ordenLlegada.
```

Tokens:

```text
Equipos terminados:
1er lugar: 5 tokens
2do lugar: 4 tokens
3er lugar o mas: 3 tokens

Equipos no terminados:
80% a 99%: 2 tokens
40% a 79%: 1 token
0% a 39%: 0 tokens
```

Si dos equipos no terminan y tienen el mismo porcentaje, pueden ordenarse por `ordenLlegada`, pero reciben los mismos tokens.

### CSV de sopa

Entrada:

```text
data/equiposSimulados.csv
```

Salida:

```text
output/Ranking.csv
```

Columnas de salida:

```text
posicion
nombreEquipo
tokensEmpatia
tokensCreatividad
tokensEvaluacion
tokensTotales
tiempoGlobalSegundos
tiempoSopaSegundos
porcentajeSopa
bonusEspera
posicionSopa
```

## Juego 2 - Bubble Map

CLI:

```bash
python -m cli.ejecutarSesionBubbleMap
```

Prueba rapida:

```bash
python -m cli.ejecutarSesionBubbleMap --duracion 10 --mostrar-ranking 0
```

Archivos:

```text
cli/ejecutarSesionBubbleMap.py
juegos/mapaEmpatia.py
puntajes/reglaPuntajeMapaEmpatia.py
competencia/csvBubbleMap.py
data/equiposSimuladosBubbleMap.csv
  output/RankingBubbleMap.csv
  output/RankingGeneral.csv
```

### Flujo de Bubble Map

1. Se inicia la sesion y la etapa.
2. Se cargan equipos simulados.
3. Se crea `Equipo Usuario`.
4. Se muestran las 5 preguntas.
5. Bajo cada pregunta se muestran los apendices ingresados, en orden.
6. El usuario elige que pregunta responder.
7. Dentro de una pregunta puede agregar apendices, ver criterios o volver.
8. Desde el menu principal puede finalizar la etapa.
9. Si finaliza y quedan al menos 5 segundos, se habilita buscaminas.
10. Si finaliza y quedan menos de 5 segundos, espera ranking.
11. Si no finaliza antes del cierre, se guarda lo hecho y se penaliza por no finalizacion.
12. Al cierre se calculan tokens, ranking y CSV.

### Preguntas

```text
gustos     -> Que le gusta y que no le gusta?
problemas  -> Que obstaculos esta enfrentando?
miedos     -> Que siente respecto a lo que le esta pasando?
contexto   -> Que le dicen los demas?
hobbies    -> Cuales son sus hobbies?
```

### Visualizacion durante Bubble Map

Durante el juego no se muestra si una pregunta esta completa, valida o ideal.

Solo se muestra:

```text
- pregunta;
- apendices ya ingresados;
- criterios breves;
- opciones.
```

Esto evita que el usuario reciba evaluacion en vivo y reduce confusion. La retroalimentacion aparece al final.

### Regla de puntaje Bubble Map

Definiciones:

```text
Apendice basura: 1 a 7 caracteres.
Apendice valido: 8 a 100 caracteres.
Apendice ideal: 40 a 60 caracteres.
Apendice excesivo: mas de 100 caracteres.
Pregunta completa: al menos 1 apendice valido.
Pregunta desarrollada: 2 o mas apendices validos.
Pregunta superficial: exactamente 1 apendice valido.
```

Calculo:

```text
+1 por cada pregunta completa.
+1 si finalizo explicitamente dentro del tiempo o justo al limite.
-1 si no finalizo explicitamente.
+1 si 4 o mas preguntas tienen todos sus apendices entre 40 y 60 caracteres.
+1 si 3 o mas preguntas tienen 2 o mas apendices validos.
-1 si 3 o mas preguntas tienen exactamente 1 apendice valido.
-1 si hay 3 o mas apendices basura en todo el mapa.
-1 si hay 3 o mas apendices excesivos en todo el mapa.
```

Bonus competitivo:

```text
+2 si el equipo esta dentro del top 3 de indicadores de contenido
y tambien dentro del top 3 de tiempos de finalizacion.
```

Este bonus solo se calcula al cierre oficial de la etapa.

Buscaminas:

```text
+0 o +1 token, segun desempeno en buscaminas.
Solo se habilita si finalizo y quedan al menos 5 segundos.
```

### Resultado final Bubble Map

Debajo del ranking se muestra:

```text
Tokens Bubble Map
Bonus excelencia y velocidad
Bonus buscaminas
Preguntas respondidas con aporte valido
Fortalezas
A mejorar
```

La retroalimentacion es breve y enfocada.

### CSV de Bubble Map

Entrada:

```text
data/equiposSimuladosBubbleMap.csv
```

Salida:

```text
output/RankingBubbleMap.csv
```

Columnas de salida:

```text
posicion
nombreEquipo
tokensEmpatia
tokensCreatividad
tokensEvaluacion
tokensTotales
tiempoGlobalSegundos
tiempoBubbleMapSegundos
finalizoBubbleMap
preguntasCompletas
preguntasDetalleIdeal
preguntasDesarrolladas
preguntasSuperficiales
apendicesBasura
apendicesExcesivos
puntajeContenidoBubbleMap
bonusExcelenciaVelocidad
bonusEspera
tokensBubbleMap
```

## Juego 3 - LEGO MVP

CLI:

```bash
python -m cli.ejecutarSesionLego
```

Prueba rapida:

```bash
python -m cli.ejecutarSesionLego --duracion 10 --mostrar-ranking 0
```

Archivos:

```text
cli/ejecutarSesionLego.py
puntajes/reglaPuntajeLego.py
competencia/csvLego.py
data/equiposSimuladosLego.csv
output/RankingLego.csv
output/RankingGeneral.csv
```

### Objetivo LEGO

La etapa simula la carga de una imagen del MVP construido con LEGO.

En terminal, la carga se representa ingresando un nombre o ruta:

```text
mvp_equipo.jpg
```

En Django debe mapearse a:

```text
Project.foto_prototipo
```

La logica de esta etapa no considera `Project.foto_grupal`.

### Puntaje LEGO

Todos los equipos que suben imagen reciben el mismo puntaje:

```text
subioImagenLego = True  -> +3 tokensCreatividad
subioImagenLego = False -> +0 tokensCreatividad
```

La etapa impacta:

```text
Team.tokens_creatividad
Team.tokens_totales
```

### Ranking previo y posicion

Antes de iniciar la etapa, la CLI muestra el ranking general actual y destaca al equipo en sesion. Esta informacion se calcula antes de sumar LEGO.

### Mensajes LEGO

La etapa usa el ranking general previo para calcular mensajes por equipo.

```text
participacionEquipo = tokensTotalesEquipo / tokensTotalesSeccion
```

Si `tokensTotalesSeccion` es 0:

```text
todos reciben ayuda 1 vez.
```

Si un equipo tiene mas del 50%:

```text
tipoMensaje = advertencia
cantidadMensajes = 1
```

Mensaje:

```text
¡Cuidado!
¡Su equipo ha generado mucho valor!
¡Los demas equipos recibiran ayuda!
```

Para los demas equipos:

```text
31% a 50% -> ayuda 1 vez
16% a 30% -> ayuda 2 veces
0% a 15%  -> ayuda 3 veces
```

Mensaje de ayuda:

```text
¡Esten atentos! Trabajen en Equipo
Envien a alguien de su equipo a la caja de legos
Pueden escoger 1 pieza extra para su MVP
```

Distribucion:

```text
1 mensaje  -> mitad de etapa
2 mensajes -> tercio y dos tercios
3 mensajes -> cuarto, mitad y tres cuartos
advertencia -> inicio de etapa
```

En la demo se muestra el mensaje del equipo en sesion. `RankingLego.csv` registra `mensajesLego` y `tipoMensajeLego` para todos los equipos.

### CSV LEGO

Entrada:

```text
data/equiposSimuladosLego.csv
```

Salida:

```text
output/RankingLego.csv
```

Columnas:

```text
posicion
nombreEquipo
tokensEmpatia
tokensCreatividad
tokensEvaluacion
tokensTotales
tokensLego
subioImagenLego
imagenLego
mensajesLego
tipoMensajeLego
```

## Juego 4 - Creacion del Pitch

CLI:

```bash
python -m cli.ejecutarSesionPitchCreacion
```

Prueba rapida:

```bash
python -m cli.ejecutarSesionPitchCreacion --duracion 10 --mostrar-ranking 0
```

Archivos:

```text
cli/ejecutarSesionPitchCreacion.py
juegos/creacionPitch.py
puntajes/reglaPuntajePitch.py
competencia/csvPitch.py
data/equiposSimuladosPitch.csv
output/RankingPitchCreacion.csv
output/RankingGeneral.csv
```

### Objetivo

Esta etapa corresponde solo a la creacion escrita del guion del pitch. No incluye exposicion ni coevaluacion.

El equipo debe completar:

```text
Nombre del producto
Desafio y empatia
Creatividad
Cierre
```

### Tiempo

Duracion por defecto:

```text
90 segundos
```

Si se acaba el tiempo, se guarda lo escrito hasta ese momento.

### Limites de caracteres

```text
Nombre del producto: 40 caracteres
Desafio y empatia: 220 caracteres
Creatividad: 220 caracteres
Cierre: 160 caracteres
```

Si el texto excede el maximo, se recorta y se informa al usuario.

### Finalizar

Existe una opcion `Finalizar`.

Si el equipo finaliza antes del cierre:

```text
- se muestra el guion final;
- no aparece buscaminas;
- queda esperando el cierre oficial de la etapa.
```

Mensaje de espera:

```text
Esperen que el tiempo acabe
Parte de Emprender es jugartela toda
En un solo momento
```

### Puntaje

La asignacion de tokens es simple:

```text
+1 por cada campo escrito.
```

Maximo:

```text
4 tokensCreatividad
```

Si no escribe nada:

```text
0 tokens
```

La etapa impacta:

```text
Team.tokens_creatividad
Team.tokens_totales
```

### CSV Pitch

Entrada:

```text
data/equiposSimuladosPitch.csv
```

Salida:

```text
output/RankingPitchCreacion.csv
```

Columnas:

```text
posicion
nombreEquipo
tokensEmpatia
tokensCreatividad
tokensEvaluacion
tokensTotales
tokensPitchCreacion
nombreProductoPitch
desafioEmpatiaPitch
creatividadPitch
cierrePitch
finalizoPitchCreacion
tiempoPitchCreacionSegundos
```

## Juego 5 - Negociacion

CLI:

```bash
python -m cli.ejecutarSesionNegociacion
```

Prueba rapida:

```bash
python -m cli.ejecutarSesionNegociacion --duracion-exposicion 1 --tolerancia-oculta 0 --mostrar-ranking 0
```

Archivos:

```text
cli/ejecutarSesionNegociacion.py
juegos/negociacion.py
puntajes/reglaPuntajeNegociacion.py
competencia/csvNegociacion.py
data/equiposNegociacion.csv
data/evaluacionesNegociacion.csv
output/RankingNegociacion.csv
output/RankingGeneral.csv
```

### Objetivo

La etapa Negociacion representa la exposicion final del emprendimiento y la evaluacion del resto de equipos.

### Orden de exposicion

Los equipos se ordenan aleatoriamente usando una semilla configurable:

```bash
--semilla 7
```

Al inicio todos ven el orden de exposicion. El equipo en sesion aparece destacado.

### Vista del equipo expositor

Cuando le toca exponer al equipo en sesion:

```text
- se muestra un temporizador pausado;
- debe presionar Enter para iniciar;
- comienza la cuenta regresiva;
- al terminar el tiempo oficial, hay una tolerancia oculta.
```

La tolerancia oculta por defecto es:

```text
6 segundos
```

Luego se muestra:

```text
Estan diciendo sobre su emprendimiento
```

### Vista de equipos que evaluan

Cuando expone otro equipo y el equipo en sesion aun no ha expuesto, se muestra la ficha del expositor:

```text
Equipo
Emprendimiento
Producto
Integrantes
Imagen equipo
Imagen MVP
```

Luego se muestran los criterios:

```text
Equipo: trabajo conjunto, coordinacion y participacion equilibrada.
Empatia: conexion con el dolor identificado en Bubble Map.
Creatividad: solucion LEGO innovadora, tecnologica y original.
Comunicacion: claridad, entusiasmo y capacidad persuasiva.
```

En la demo, las evaluaciones se cargan desde:

```text
data/evaluacionesNegociacion.csv
```

### Vista de equipos que ya expusieron

Cuando el equipo en sesion ya expuso, durante los turnos restantes ve:

```text
Espera a que el resto termine
Pronto sabremos
El emprendimiento ganador
```

### Puntaje de negociacion

La demo replica la logica del sistema actual usando el promedio de `puntajeEquipo` recibido.

```text
promedio < 2.5      -> 0 tokensEvaluacion
2.5 a 3.49          -> 2 tokensEvaluacion
3.5 a 4.49          -> 4 tokensEvaluacion
4.5 o mas           -> 6 tokensEvaluacion
```

Un equipo no puede evaluarse a si mismo. Las autoevaluaciones se filtran.

### CSV Negociacion

Salida:

```text
output/RankingNegociacion.csv
```

Columnas:

```text
posicion
nombreEquipo
tokensEmpatia
tokensCreatividad
tokensEvaluacion
tokensTotales
ordenExposicion
promedioEvaluacionRecibida
evaluacionesRecibidas
tokensNegociacion
```

## Pruebas realizadas

Compilacion general:

```bash
logiJuegos/bin/python -m compileall competencia juegos puntajes espera cli
```

Prueba sopa completa:

```bash
printf 'cliente\nproblema\nidea\nprototipo\nempatia\nequipo\npitch\nvalor\nfin\n' | logiJuegos/bin/python -m cli.ejecutarSesionSopa --duracion 2
```

Prueba sopa con palabra tardia:

```bash
bash -c '{ sleep 2; printf "cliente\n"; } | logiJuegos/bin/python -m cli.ejecutarSesionSopa --duracion 1'
```

Resultado esperado:

```text
La palabra tardia no se acepta.
```

Prueba Bubble Map con respuestas y cierre:

```bash
python -m cli.ejecutarSesionBubbleMap --duracion 10 --mostrar-ranking 0
```

Prueba Bubble Map sin finalizar:

```bash
python -m cli.ejecutarSesionBubbleMap --duracion 1 --mostrar-ranking 0
```

Resultado esperado:

```text
Se guarda lo ingresado.
No se habilita buscaminas.
Se aplica penalizacion por no finalizar.
```

Prueba LEGO con imagen:

```bash
printf '1\nmvp_usuario.jpg\n' | logiJuegos/bin/python -m cli.ejecutarSesionLego --duracion 1 --mostrar-ranking 0
```

Prueba LEGO sin imagen:

```bash
printf '3\n' | logiJuegos/bin/python -m cli.ejecutarSesionLego --duracion 1 --mostrar-ranking 0
```

Prueba creacion Pitch parcial:

```bash
printf '1\nEcoMVP\n2\nProblema y persona afectada explicados de forma breve.\n5\n' | logiJuegos/bin/python -m cli.ejecutarSesionPitchCreacion --duracion 2 --mostrar-ranking 0
```

Prueba negociacion:

```bash
printf '\n' | logiJuegos/bin/python -m cli.ejecutarSesionNegociacion --duracion-exposicion 1 --tolerancia-oculta 0 --mostrar-ranking 0 --semilla 1
```

## Equivalencia futura con Django

### General

```text
SesionJuego -> GameSession
Equipo -> Team
tokensTotales -> Team.tokens_totales
Ranking global -> consulta ordenada por tokens_totales
CLI -> views/templates/JavaScript
RankingGeneral.csv -> estado acumulado equivalente a Team.tokens_* en BD
```

### Sopa

```text
JuegoSopaLetras -> logica/servicio de etapa 1
Estado de sopa -> TeamGameSession
reglaPuntajeSopaLetras -> services/scoring.py
```

### Bubble Map

```text
MapaEmpatia -> EmpathyMap
PreguntaMapaEmpatia -> gustos/problemas/miedos/contexto/hobbies
apendices -> datos_extra o JSON equivalente
reglaPuntajeMapaEmpatia -> services/scoring.py
tokensBubbleMap -> Team.tokens_empatia
```

### LEGO MVP

```text
imagenLego -> Project.foto_prototipo
subioImagenLego -> bool(Project.foto_prototipo)
tokensLego -> aporte de etapa 3 a Team.tokens_creatividad
mensajesLego/tipoMensajeLego -> servicio de mensajes de etapa basado en ranking previo
```

No se debe eliminar `Project.foto_grupal`; simplemente no participa en esta logica.

### Creacion del Pitch

```text
CreacionPitch -> estructura temporal para armar Pitch.guion
nombreProductoPitch -> parte del guion o campo futuro si se decide extender Pitch/Project
desafioEmpatiaPitch -> parte del guion
creatividadPitch -> parte del guion
cierrePitch -> parte del guion
tokensPitchCreacion -> aporte a Team.tokens_creatividad
```

En Django, el texto final puede guardarse en:

```text
Pitch.guion
```

con estructura:

```text
Producto:
...

Desafio y empatia:
...

Creatividad:
...

Cierre:
...
```

### Negociacion

```text
ordenExposicion -> orden temporal de presentacion en la sesion.
EvaluacionNegociacion -> Evaluation del sistema real.
puntajeEquipo -> Evaluation.puntaje_equipo.
tokensNegociacion -> aporte final a Team.tokens_evaluacion.
```

En Django, las evaluaciones deben persistirse en:

```text
Evaluation
```

Manteniendo la restriccion:

```text
unique_together = (sesion, evaluador, evaluado)
```

La vista debe impedir autoevaluacion:

```text
evaluador != evaluado
```

Reglas que deben preservarse en Django:

```text
- backend controla tiempo;
- no se aceptan acciones despues del cierre;
- finalizar es una senal explicita;
- buscaminas aparece solo si quedan al menos 5 segundos;
- ranking destaca siempre al equipo en sesion;
- ranking se muestra 15 segundos por defecto;
- ranking final/global usa Team.tokens_totales.
```
