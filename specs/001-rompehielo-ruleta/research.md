# Research: Backend de Ruleta para Rompehielo

## Decision 1: Implementar `RouletteEngine` como servicio stateless con catalogo en memoria

- **Decision**: Crear `RouletteEngine` en `proyecIngSoft/etapasJuego/services/roulette.py`
  con un catalogo hardcodeado de preguntas y tres metodos publicos:
  `get_questions()`, `select_question(available_ids)` y `handle_error(context)`.
- **Rationale**: El spec y el input del usuario ya fijan que el estado del turno
  vive en el cliente y que la fuente de datos debe poder migrarse a modelo Django
  sin romper la interfaz publica. Un servicio stateless permite esa evolucion sin
  acoplar la vista a detalles de almacenamiento.
- **Alternatives considered**:
  - Guardar preguntas y ciclo en sesion Django: rechazado porque contradice la
    decision de arquitectura de mantener el estado en JS.
  - Implementar funciones sueltas en `views.py`: rechazado porque mezclaria
    logica de dominio con capa HTTP y dificultaria la futura sustitucion por BD.
  - Reutilizar `scoring.py` o `pitch_ai.py`: rechazado porque no comparten
    responsabilidad de dominio con rompehielo.

## Decision 2: Reutilizar la URL existente `rompehielo` con modo dual HTML/JSON

- **Decision**: Mantener `GET /etapasJuego/tablet/rompehielo/` como entrada
  unica y responder JSON cuando llegue `?format=json` o un encabezado `Accept:
  application/json`; en cualquier otro caso, renderizar el template actual.
- **Rationale**: El usuario pidio no crear una URL nueva si la actual ya existe.
  La vista dual evita dispersar contratos, mantiene compatibilidad hacia atras
  con el template y habilita bootstrap AJAX para el frontend.
- **Alternatives considered**:
  - Crear `/api/rompehielo/questions/`: rechazado porque agrega una ruta nueva
    sin necesidad funcional.
  - Responder JSON solo por query param: rechazado porque el requerimiento
    menciona header o parametro; soportar ambos reduce friccion de integracion.
  - Responder JSON solo por header: rechazado porque el ejemplo del usuario usa
    explicitamente `?format=json`.

## Decision 3: Seleccion defensiva con reinicio automatico del ciclo

- **Decision**: `select_question(available_ids)` filtrara el catalogo por los IDs
  recibidos; si el subconjunto queda vacio, reutilizara todos los IDs del
  catalogo y seleccionara aleatoriamente desde ahi; nunca lanzara excepcion por
  lista vacia.
- **Rationale**: La especificacion aclarada exige reinicio al agotarse la ruleta
  y el usuario definio que el cliente controla el ciclo. El backend debe ser
  tolerante a entradas vacias o parciales para no bloquear la demo.
- **Alternatives considered**:
  - Lanzar `ValueError` si no hay IDs: rechazado porque rompe el criterio de
    recuperacion y obligaria a manejo extra en la vista.
  - Devolver `None`: rechazado porque complica el contrato y obliga a ramas
    adicionales en el frontend.

## Decision 4: Usar `django.test.TestCase` en `etapasJuego/tests.py`

- **Decision**: Agregar pruebas del engine y de la vista en el archivo existente
  `proyecIngSoft/etapasJuego/tests.py`.
- **Rationale**: El proyecto ya usa el patron `django.test.TestCase` por app y
  el archivo actual esta disponible para crecer. Esto minimiza dispersion y
  cumple la higiene de codigo.
- **Alternatives considered**:
  - Crear una nueva carpeta `tests/`: rechazado porque no sigue el patron actual
    del repositorio.
  - No agregar pruebas: rechazado porque la constitucion exige no regresion
    verificable.
