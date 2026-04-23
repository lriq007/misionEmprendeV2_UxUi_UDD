# Quickstart: Ruleta de Rompehielo para Tablet

## Objetivo

Implementar la experiencia completa de ruleta en
`/etapasJuego/tablet/rompehielo/`: mantener el render HTML existente, entregar
el catalogo de preguntas en JSON para bootstrap del cliente y actualizar el
template/CSS/JS de la pantalla para mostrar ruleta central, accion dominante de
turno, mensajes guiados y manejo de errores/reintento.

## Archivos objetivo

- Crear `proyecIngSoft/etapasJuego/services/roulette.py`
- Modificar `proyecIngSoft/etapasJuego/views.py`
- Modificar `proyecIngSoft/etapasJuego/tests.py`
- Modificar `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`
- Modificar `proyecIngSoft/etapasJuego/static/etapasJuego/css/rompehielo.css`
- Modificar `proyecIngSoft/etapasJuego/static/etapasJuego/js/rompehielo.js`
- Modificar `proyecIngSoft/etapasJuego/services/__init__.py` si se usa como
  fachada del paquete

## Pasos de implementacion

1. Crear `RouletteEngine` con un catalogo hardcodeado de 8-12 preguntas en
   espanol para estudiantes universitarios.
2. Implementar en backend:
   - `get_questions() -> list[dict]`
   - `select_question(available_ids: list[int]) -> dict`
   - `handle_error(context: str) -> dict`
3. Actualizar `rompehielo(request)` para:
   - renderizar `etapasJuego/rompehielo.html` por defecto
   - devolver `JsonResponse({"success": True, "questions": [...]})` cuando se
     solicite JSON con `?format=json` o `Accept: application/json`
4. Mantener la URL existente `path("tablet/rompehielo/", views.rompehielo, name="rompehielo")`
   sin crear una nueva ruta.
5. Rehacer el frontend existente para:
   - mostrar una ruleta central con segmentos visibles para las preguntas
   - sostener una unica accion primaria dominante: `Siguiente turno`
   - mostrar la pregunta elegida en una zona principal legible
   - mostrar `Comparte con tus companeros la respuesta`
   - mostrar luego `Entregale la tablet al siguiente companero`
   - bloquear toques repetidos mientras el turno se resuelve
   - mostrar error accionable y permitir reintento en la misma pantalla
6. Agregar pruebas para:
   - `RouletteEngine().get_questions()`
   - `RouletteEngine().select_question([])`
   - `RouletteEngine().handle_error("test")`
   - `GET /etapasJuego/tablet/rompehielo/`
   - `GET /etapasJuego/tablet/rompehielo/?format=json`

## Verificacion local

Desde `proyecIngSoft/`:

```bash
python manage.py test etapasJuego
```

Verificacion manual sugerida:

```bash
python manage.py runserver
```

Luego abrir:

- HTML: `http://127.0.0.1:8000/etapasJuego/tablet/rompehielo/`
- JSON: `http://127.0.0.1:8000/etapasJuego/tablet/rompehielo/?format=json`

## Validacion manual recomendada

### MVP de ruleta

1. Abrir la pantalla HTML en tablet portrait `768-1023px`.
2. Confirmar que existe una ruleta central y un unico boton dominante
   `Siguiente turno`.
3. Presionar el boton y validar feedback visible inmediato en menos de `300ms`.
4. Confirmar que aparece una pregunta activa legible y que no se repite hasta
   agotar el ciclo.
5. Confirmar que al terminar el ciclo la ruleta vuelve a quedar disponible con
   todas las preguntas.

### Mensajes guiados

1. Ejecutar un turno.
2. Confirmar que aparece `Comparte con tus companeros la respuesta` sin tapar la
   pregunta.
3. Confirmar que aparece luego `Entregale la tablet al siguiente companero` en
   una zona visualmente distinta.
4. Confirmar que ambas ayudas siguen legibles en tablet landscape
   `1024-1279px`.

### Error y reintento

1. Simular fallo del bootstrap JSON o del estado del turno.
2. Confirmar que la pantalla permanece en `rompehielo`.
3. Confirmar que aparece un mensaje accionable.
4. Confirmar que el mismo boton principal permite reintentar.

### Temporizador y no regresion

1. Confirmar que el temporizador sigue visible durante la dinamica.
2. Rotar la tablet durante un turno activo y validar que no se pierde la
   pregunta ni la accion principal.
3. Esperar el timeout y confirmar que el overlay sigue permitiendo avanzar a
   `etapa1`.

### Calidad visual

1. Comparar visualmente la pantalla con
   `proyecIngSoft/etapasJuego/templates/etapasJuego/seleccion_modalidad.html`
   y `proyecIngSoft/login/templates/login/home_estudiante.html`.
2. Confirmar jerarquia clara, ayuda contextual, estados visibles y ausencia de
   overflow en tablet portrait, tablet landscape y escritorio `1280px+`.
3. Alcance movil `360-767px`: fuera del alcance formal de esta iteracion; la
   aprobacion se limita a tablet portrait, tablet landscape y escritorio.

## Resultado esperado del modo JSON

- HTTP 200
- `Content-Type` con `application/json`
- `success: true`
- `questions` como lista de dicts con `id` y `text`
