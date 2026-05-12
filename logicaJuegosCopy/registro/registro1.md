# Registro 1 - Estado actual del sistema de logica de juegos

Fecha de registro: 2026-05-09

Este documento describe el estado actual del proyecto `logicaJuegos`. Su objetivo es servir como respaldo tecnico para reconstruir la version actual si el sistema falla o si se necesita comparar cambios futuros.

## Objetivo del proyecto

El proyecto implementa logica pura de mini juegos en Python, ejecutable desde terminal, para luego migrarla al proyecto Django real.

La idea principal es separar:

- logica del juego;
- cronometros;
- calculo de tokens;
- ranking;
- simulacion de equipos;
- exportacion de resultados.

El proyecto no levanta un servidor. El archivo CLI simula por terminal el flujo que luego estaria distribuido entre `views.py`, `models.py`, `services.py`, templates y JavaScript en Django.

## Entorno virtual

El entorno virtual se llama:

```bash
logiJuegos
```

Se activa con:

```bash
source logiJuegos/bin/activate
```

Version de Python usada al crear el entorno:

```text
Python 3.12.3
```

Actualmente no se instalaron librerias externas. El sistema usa solo librerias estandar de Python.

## Librerias usadas

Librerias estandar utilizadas:

- `argparse`: leer argumentos del CLI, especialmente `--duracion`.
- `csv`: cargar equipos simulados y exportar ranking final.
- `dataclasses`: declarar clases simples de datos.
- `pathlib`: manejar rutas de archivos.
- `random`: generar sopa de letras y minas.
- `select`: leer entradas por terminal con tiempo limite real.
- `string`: obtener letras del alfabeto.
- `sys`: leer `stdin`.
- `time.monotonic`: medir duraciones de forma estable.
- `time.sleep`: esperar el cierre de etapa cuando corresponde.

## Estructura actual

```text
logicaJuegos/
  cli/
    __init__.py
    ejecutarSesionSopa.py

  competencia/
    __init__.py
    cronometro.py
    csvRanking.py
    equipo.py
    sesionJuego.py

  data/
    equiposSimulados.csv

  espera/
    __init__.py
    buscaminasEspera.py

  juegos/
    __init__.py
    juegoSopaLetras.py

  output/
    Ranking.csv

  puntajes/
    __init__.py
    ranking.py
    reglaPuntajeSopaLetras.py

  registro/
    registro1.md

  README.md
  .gitignore
```

## Archivo ejecutable principal

El flujo completo se ejecuta desde:

```text
cli/ejecutarSesionSopa.py
```

Comando normal:

```bash
python -m cli.ejecutarSesionSopa
```

Comando con duracion personalizada:

```bash
python -m cli.ejecutarSesionSopa --duracion 10
```

`--duracion` define la duracion de la etapa en segundos. Por defecto son `120` segundos.

## Flujo general actual

1. Se carga el CSV de equipos simulados desde `data/equiposSimulados.csv`.
2. Se crea un `Equipo Usuario`, que representa al equipo que juega por terminal.
3. Se crea una `SesionJuego`.
4. Se inicia el cronometro global.
5. Se inicia el cronometro de etapa.
6. Se genera una sopa de letras con 8 palabras.
7. El usuario ingresa palabras por terminal.
8. Si el usuario termina la sopa antes del cierre de la etapa, se habilita el buscaminas de espera.
9. Al acabarse el tiempo, se cierra la etapa.
10. Se calculan tokens de sopa y bonus.
11. Se calcula ranking global.
12. Se exporta `output/Ranking.csv`.

## Cronometros

El archivo `competencia/cronometro.py` define la clase `Cronometro`.

Campos:

- `nombre`
- `inicio`
- `fin`

Metodos principales:

- `iniciar()`
- `detener()`
- `segundosTranscurridos()`
- `textoTranscurrido()`

La medicion usa `time.monotonic()` para evitar problemas si cambia el reloj del sistema.

Existen dos cronometros en la sesion:

- `cronometroGlobal`: mide la sesion completa.
- `cronometroEtapa`: mide la etapa actual.

En esta primera version, como solo hay un juego principal, ambos tiempos pueden ser muy parecidos.

## Control estricto del tiempo

El sistema evita que se ingresen jugadas despues de acabado el tiempo.

La funcion relevante esta en `cli/ejecutarSesionSopa.py`:

```python
pedirEntradaConTiempo(mensaje, segundosDisponibles)
```

Esta funcion usa `select` para esperar entrada solo durante los segundos restantes de la etapa.

Si el usuario espera demasiado:

```text
Tiempo agotado. No se aceptan mas jugadas.
```

Ademas, despues de recibir una entrada, el sistema vuelve a revisar:

```python
sesion.etapaTerminada()
```

Esto impide que una palabra escrita tarde sea aceptada.

Esta regla es importante para la migracion a Django: el backend debe ser la autoridad del tiempo, no solo el temporizador visual del frontend.

## Equipo

El archivo `competencia/equipo.py` define la clase `Equipo`.

Campos actuales:

- `nombreEquipo`
- `tokensEmpatia`
- `tokensCreatividad`
- `tokensEvaluacion`
- `tiempoGlobalSegundos`
- `tiempoSopaSegundos`
- `porcentajeSopa`
- `bonusEspera`
- `posicionSopa`
- `ordenLlegada`

Propiedad calculada:

```python
tokensTotales = tokensEmpatia + tokensCreatividad + tokensEvaluacion
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

El archivo `competencia/sesionJuego.py` define la clase `SesionJuego`.

Representa conceptualmente a `GameSession` del proyecto Django.

Campos:

- `nombreSesion`
- `duracionEtapaSegundos`
- `equipos`
- `cronometroGlobal`
- `cronometroEtapa`

Metodos:

- `iniciarSesion()`
- `iniciarEtapa()`
- `finalizarSesion()`
- `agregarEquipo()`
- `segundosRestantesEtapa()`
- `etapaTerminada()`

## Sopa de letras

El archivo `juegos/juegoSopaLetras.py` define la clase `JuegoSopaLetras`.

Reglas:

- minimo 8 palabras;
- maximo 15 palabras;
- tablero por defecto de 15x15;
- palabras normalizadas a mayuscula;
- ubicacion horizontal, vertical y diagonal;
- relleno automatico con letras aleatorias.

Metodos principales:

- `generarTablero()`
- `validarPalabra(palabra)`
- `imprimirTablero()`
- `imprimirPistas(encontradas)`

Las palabras actuales del demo estan en `cli/ejecutarSesionSopa.py`:

```python
PALABRAS_SOPA = [
    "cliente",
    "problema",
    "idea",
    "prototipo",
    "empatia",
    "equipo",
    "pitch",
    "valor",
]
```

## Buscaminas de espera

El archivo `espera/buscaminasEspera.py` define la clase `BuscaminasEspera`.

Este juego se muestra solo si el equipo termina la sopa antes del cierre de la etapa.

Configuracion actual:

- tablero de 4x4;
- 8 minas;
- bonus maximo de 1 token.

Metodos principales:

- `generarTablero()`
- `abrirCasilla(fila, columna)`
- `calcularBonus()`
- `imprimirTableroVisible()`

Regla de bonus:

- el bonus maximo es 1 token;
- para obtenerlo se debe abrir al menos el 50% de las casillas seguras;
- si se pisa una mina, el juego termina y el bonus queda en 0.

El bonus se registra durante la etapa y se suma oficialmente al cerrar la etapa.

## Regla de puntaje de sopa

El archivo `puntajes/reglaPuntajeSopaLetras.py` calcula el ranking interno de la sopa y asigna tokens.

Orden de ranking interno:

1. Equipos que terminaron, ordenados por menor tiempo.
2. Equipos que no terminaron, ordenados por mayor porcentaje.
3. En empates de porcentaje, se usa `ordenLlegada`.

Regla de tokens:

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

Observacion importante:

Si dos equipos no terminaron y tienen el mismo porcentaje, pueden quedar ordenados por `ordenLlegada`, pero reciben el mismo numero de tokens.

Ejemplo actual en `data/equiposSimulados.csv`:

```text
Equipo Gamma: 80%
Equipo Zeta: 80%
```

Ambos reciben los mismos tokens por sopa.

## Ranking global

El archivo `puntajes/ranking.py` ordena el ranking global.

Criterios actuales:

1. Mayor `tokensTotales`.
2. Menor `tiempoGlobalSegundos`.
3. Mejor `posicionSopa`.
4. Mayor `porcentajeSopa`.
5. Menor `ordenLlegada`.

El criterio principal replica el sistema Django actual:

```text
Team.tokens_totales
```

## Equipos simulados

El archivo `data/equiposSimulados.csv` contiene equipos predefinidos para comparar al equipo que juega por terminal.

Columnas:

```csv
nombreEquipo,tokensEmpatia,tokensCreatividad,tokensEvaluacion,tiempoGlobalSegundos,tiempoSopaSegundos,porcentajeSopa,bonusEspera,ordenLlegada
```

Estos equipos permiten simular ranking sin tener una base de datos ni multiples usuarios jugando al mismo tiempo.

## Exportacion de ranking

El archivo `competencia/csvRanking.py` contiene:

- `cargarEquiposSimulados(rutaCsv)`
- `exportarRanking(rutaCsv, ranking)`

Al finalizar la etapa se genera:

```text
output/Ranking.csv
```

Columnas exportadas:

```csv
posicion,nombreEquipo,tokensEmpatia,tokensCreatividad,tokensEvaluacion,tokensTotales,tiempoGlobalSegundos,tiempoSopaSegundos,porcentajeSopa,bonusEspera,posicionSopa
```

Este CSV es el respaldo visible del resultado final de la simulacion.

## Pruebas realizadas

Compilacion:

```bash
logiJuegos/bin/python -m compileall competencia juegos puntajes espera cli
```

Prueba rapida de flujo completo:

```bash
printf 'cliente\nproblema\nidea\nprototipo\nempatia\nequipo\npitch\nvalor\nfin\n' | logiJuegos/bin/python -m cli.ejecutarSesionSopa --duracion 2
```

Prueba de tiempo agotado sin entrada:

```bash
logiJuegos/bin/python -m cli.ejecutarSesionSopa --duracion 1
```

Prueba de palabra tardia:

```bash
bash -c '{ sleep 2; printf "cliente\n"; } | logiJuegos/bin/python -m cli.ejecutarSesionSopa --duracion 1'
```

Resultado esperado:

- la palabra llega despues del tiempo;
- no se acepta;
- el equipo queda con 0% si no habia registrado progreso previo.

## Equivalencia futura con Django

La migracion futura deberia respetar esta separacion:

```text
SesionJuego -> GameSession
Equipo -> Team
Estado de sopa -> TeamGameSession
ReglaPuntajeSopaLetras -> service de scoring
Ranking global -> consulta/servicio que ordena Team.tokens_totales
CLI -> views.py + templates + JavaScript
```

Regla critica para Django:

```text
El backend debe rechazar jugadas si la etapa ya termino.
```

El frontend puede mostrar el temporizador, pero no debe ser la fuente de verdad.

## Estado actual del sistema

El sistema actual permite:

- ejecutar una sesion por terminal;
- jugar sopa de letras;
- medir tiempo global;
- medir tiempo por etapa;
- cerrar automaticamente por tiempo;
- impedir palabras ingresadas tarde;
- habilitar buscaminas si se termina antes;
- calcular bonus limitado;
- calcular tokens;
- diferenciar equipos por porcentaje;
- dar mismos tokens a equipos no terminados con igual porcentaje;
- generar ranking global;
- exportar `output/Ranking.csv`.

## Actualizacion - Bubble Map

Se agrego una segunda etapa ejecutable por terminal:

```bash
python -m cli.ejecutarSesionBubbleMap
```

Para pruebas rapidas:

```bash
python -m cli.ejecutarSesionBubbleMap --duracion 10 --mostrar-ranking 0
```

El argumento `--mostrar-ranking` controla cuantos segundos queda visible el ranking final. Por defecto son 15 segundos.

### Archivos agregados para Bubble Map

```text
cli/ejecutarSesionBubbleMap.py
competencia/csvBubbleMap.py
data/equiposSimuladosBubbleMap.csv
juegos/mapaEmpatia.py
puntajes/reglaPuntajeMapaEmpatia.py
output/RankingBubbleMap.csv
```

### Flujo de Bubble Map

1. Se inicia una sesion con cronometro global y cronometro de etapa.
2. Se carga un CSV de equipos simulados.
3. Se crea el `Equipo Usuario`.
4. La terminal muestra las 5 preguntas del Bubble Map.
5. Bajo cada pregunta se muestran los apendices ingresados, en orden del primero al mas reciente.
6. El usuario puede escoger que pregunta responder.
7. Dentro de cada pregunta puede agregar apendices, ver criterios o volver al menu.
8. Desde el menu principal puede finalizar explicitamente la etapa.
9. Si finaliza y quedan al menos 5 segundos, se habilita buscaminas de espera.
10. Si finaliza y quedan menos de 5 segundos, pasa directo a espera del ranking.
11. Si se acaba el tiempo sin finalizar, se guarda lo respondido y se penaliza por no finalizacion.
12. Al cerrar la etapa se calculan tokens, ranking y CSV final.

### Preguntas del Bubble Map

```text
gustos     -> Que le gusta y que no le gusta?
problemas  -> Que obstaculos esta enfrentando?
miedos     -> Que siente respecto a lo que le esta pasando?
contexto   -> Que le dicen los demas?
hobbies    -> Cuales son sus hobbies?
```

Cada pregunta puede tener multiples apendices.

### Reglas de visualizacion durante el juego

Durante el juego no se muestra si una pregunta esta completa, valida o ideal. Solo se muestran:

```text
- pregunta;
- apendices ingresados;
- criterios breves;
- opciones de accion.
```

Esto evita confundir al usuario y evita revelar evaluacion en vivo. La retroalimentacion aparece al final.

### Regla de puntaje Bubble Map

La regla busca premiar contenido, finalizacion y buen uso del tiempo sin permitir que la velocidad domine.

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

Ademas existe un bonus competitivo:

```text
+2 si el equipo esta dentro del top 3 de indicadores de contenido
y tambien dentro del top 3 de tiempos de finalizacion.
```

Este bonus solo puede calcularse al cierre oficial de la etapa, porque necesita comparar todos los equipos.

### Buscaminas de espera en Bubble Map

El buscaminas se habilita solo si:

```text
finalizoBubbleMap = True
y segundosRestantesEtapa >= 5
```

Si quedan menos de 5 segundos:

```text
No se muestra buscaminas.
El equipo pasa directo a espera del ranking.
```

El bonus maximo del buscaminas sigue siendo 1 token.

### Ranking Bubble Map

El ranking de Bubble Map se exporta en:

```text
output/RankingBubbleMap.csv
```

Columnas principales:

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

El ranking siempre destaca al equipo en sesion y muestra su posicion.

### Retroalimentacion final

Debajo del ranking se muestra el resultado del equipo en sesion:

```text
Tokens Bubble Map
Bonus excelencia y velocidad
Bonus buscaminas
Preguntas respondidas con aporte valido
Fortalezas
A mejorar
```

La retroalimentacion se mantiene breve para que sea usable en terminal y luego facil de adaptar a frontend.

### Equivalencia con Django para Bubble Map

```text
MapaEmpatia -> EmpathyMap
PreguntaMapaEmpatia -> campos gustos/problemas/miedos/contexto/hobbies
apendices -> datos_extra o estructura JSON equivalente
reglaPuntajeMapaEmpatia -> services/scoring.py
tokensBubbleMap -> Team.tokens_empatia
RankingBubbleMap.csv -> ranking parcial/global basado en Team.tokens_totales
```

La migracion a Django debe preservar estas reglas:

```text
- el backend controla el tiempo;
- no se aceptan respuestas despues del cierre;
- finalizar es una senal explicita;
- el buscaminas solo aparece si quedan al menos 5 segundos;
- el ranking se muestra 15 segundos;
- el equipo en sesion siempre se destaca.
```
