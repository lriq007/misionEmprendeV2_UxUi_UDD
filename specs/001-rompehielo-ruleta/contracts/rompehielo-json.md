# Contract: Rompehielo Dual HTML/JSON Endpoint

## Route

- **Name**: `rompehielo`
- **Path**: `/etapasJuego/tablet/rompehielo/`
- **Method**: `GET`

## Modes

### 1. HTML mode

- **Trigger**: Request sin `?format=json` y sin preferencia explicita por JSON
- **Response**: Render de `etapasJuego/rompehielo.html`
- **Status**: `200 OK`

### 2. JSON mode

- **Trigger**:
  - `GET /etapasJuego/tablet/rompehielo/?format=json`
  - o header `Accept: application/json`
- **Response**: `JsonResponse`
- **Status**: `200 OK`
- **Content-Type**: `application/json`

## Success Payload

```json
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "text": "¿Que habilidad tuya crees que el grupo aun no conoce?"
    }
  ]
}
```

## Error Payload

Generado mediante `RouletteEngine.handle_error(context)`.

```json
{
  "success": false,
  "message": "No pudimos cargar las preguntas del rompehielo. Intenta nuevamente.",
  "context": "get_questions"
}
```

## Engine Contract

### `RouletteEngine.get_questions() -> list[dict]`

- Devuelve el catalogo completo de preguntas.
- Cada item contiene al menos:
  - `id: int`
  - `text: str`

### `RouletteEngine.select_question(available_ids: list[int]) -> dict`

- Filtra por IDs disponibles en el ciclo actual.
- Si `available_ids` llega vacio o no coincide con preguntas validas, reinicia
  sobre el catalogo completo.
- Nunca lanza excepcion por lista vacia.

### `RouletteEngine.handle_error(context: str) -> dict`

- Devuelve:
  - `success: false`
  - `message: str`
  - `context: str`

## Compatibility Notes

- No se crea URL nueva.
- No se persiste estado de ruleta en sesion Django.
- La seleccion de turnos y bloqueo del boton siguen siendo responsabilidad del
  cliente.
