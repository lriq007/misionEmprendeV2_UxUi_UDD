# Data Model: Backend de Ruleta para Rompehielo

## Entity: RouletteQuestion

- **Purpose**: Representa una pregunta disponible para la ruleta de rompehielo.
- **Shape**:
  - `id: int`
  - `text: str`
- **Source**: Catalogo hardcodeado dentro de `RouletteEngine` en esta iteracion.
- **Validation**:
  - `id` debe ser unico dentro del catalogo.
  - `text` debe ser no vacio y legible para estudiantes universitarios.
  - El catalogo debe contener entre 8 y 12 preguntas.

## Entity: QuestionCatalog

- **Purpose**: Coleccion completa de `RouletteQuestion` expuesta por
  `RouletteEngine.get_questions()`.
- **Ownership**: Backend Django, solo lectura para la vista.
- **Validation**:
  - Siempre devuelve `list[dict]`.
  - Cada item incluye al menos `id` y `text`.
  - Debe poder sustituirse por una fuente de datos distinta en el futuro sin
    cambiar la interfaz publica del engine.

## Entity: AvailableQuestionIds

- **Purpose**: Subconjunto de IDs aun no usados en el ciclo actual.
- **Ownership**: Cliente JavaScript.
- **Shape**: `list[int]`
- **Lifecycle**:
  1. El cliente inicia con todos los IDs del catalogo.
  2. Tras cada turno, elimina el ID usado.
  3. Cuando la lista queda vacia, puede enviar `[]` al backend o reiniciarse en
     cliente; `select_question([])` debe seguir funcionando.
- **Validation**:
  - Puede venir vacio.
  - Puede contener IDs invalidos o desactualizados; el engine debe degradar al
    catalogo completo en lugar de fallar.

## Entity: RouletteSelectionResult

- **Purpose**: Respuesta de `select_question(available_ids)`.
- **Shape**:
  - `id: int`
  - `text: str`
- **Validation**:
  - Siempre corresponde a una pregunta valida del catalogo.
  - Nunca es `None`.

## Entity: RouletteErrorPayload

- **Purpose**: Respuesta serializable de `handle_error(context)` para la vista.
- **Shape**:
  - `success: bool` = `False`
  - `message: str`
  - `context: str`
- **Usage**: Se devuelve cuando la vista no puede completar una operacion
  relacionada con rompehielo.
- **Validation**:
  - `message` debe ser legible para usuario final.
  - `context` conserva el origen tecnico o funcional del error.

## State Notes

- No existe entidad persistida de turno en backend en esta iteracion.
- No se agregan modelos Django ni migraciones.
- La transicion de ciclo ocurre implicitamente:
  - `available_ids` no vacio -> seleccionar dentro del subconjunto
  - `available_ids` vacio o invalido -> reiniciar al catalogo completo
