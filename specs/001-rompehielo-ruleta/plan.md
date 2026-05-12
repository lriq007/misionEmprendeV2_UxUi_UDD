# Implementation Plan: Ruleta de Rompehielo para Tablet

**Branch**: `[001-actualiza-modulo-etapas-juego]` | **Date**: 2026-04-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-rompehielo-ruleta/spec.md`

## Summary

Esta iteracion implementa la ruleta de rompehielo completa sobre la pantalla
existente `rompehielo` dentro de `etapasJuego`: un `RouletteEngine` nuevo en
`services/roulette.py` para exponer un catalogo de preguntas reutilizable, una
actualizacion de `views.py` para soportar bootstrap JSON en la misma URL, y una
reestructuracion del frontend existente en `rompehielo.html`,
`rompehielo.css` y `rompehielo.js` para mostrar una ruleta central, una accion
primaria dominante de siguiente turno, mensajes guiados para responder y pasar
la tablet, y estados visuales consistentes con la constitucion. La
implementacion sigue siendo stateless en backend y no requiere migraciones,
pero el alcance real incluye trabajo de layout tablet-first, control de estado
en JS y validacion responsive.

## Technical Context

**Language/Version**: Python 3.12.3, HTML5, CSS3, JavaScript ES2020  
**Primary Dependencies**: Django 5.2.7, stdlib de Python (`random`, `typing`), templates/static existentes de `etapasJuego`  
**Storage**: N/A en esta iteracion; catalogo de preguntas hardcodeado en memoria, sin persistencia de estado de turno en sesion ni BD  
**Testing**: `django.test.TestCase` ejecutado con `python manage.py test etapasJuego` mas validacion manual de UI para tablet portrait `768-1023px`, tablet landscape `1024-1279px`, rotacion de dispositivo, feedback visible < `300ms` y continuidad hacia `etapa1`  
**Target Platform**: Aplicacion web Django server-rendered consumida principalmente desde tablets compartidas; alcance aprobado para tablet/escritorio, sin soporte formal para movil `360-767px` en esta iteracion  
**Project Type**: Aplicacion web Django modular  
**Performance Goals**: Responder el bootstrap JSON de preguntas en una sola llamada GET y mantener feedback visible en la UI de turno en menos de `300ms` mediante estados perceptibles de carga, seleccion o confirmacion  
**Constraints**: No crear modelos ni migraciones; no agregar dependencias externas; mantener la URL existente `rompehielo`; no persistir estado del ciclo en backend; reutilizar los archivos Django/template/static existentes siempre que sea posible; no dejar codigo muerto ni imports sin uso; esta iteracion valida `rompehielo` solo para tablet/escritorio y excluye soporte formal para movil `360-767px`  
**Scale/Scope**: 1 servicio nuevo, 1 vista existente actualizada, 1 template actualizado, 1 archivo CSS actualizado, 1 archivo JS actualizado, 1 export opcional en `services/__init__.py`, pruebas en `etapasJuego/tests.py`, 8-12 preguntas hardcodeadas en espanol y estados de turno manejados en frontend

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Percepcion del Cliente/Jurado como Criterio Final**: PASS. El plan apunta a
  una mejora visible y demostrable de la pantalla de rompehielo: ruleta central,
  accion primaria clara, mensajes guiados y una experiencia mas ordenada para la
  demo, sin agregar complejidad de persistencia innecesaria.
- **Identidad Inmersiva y Experiencia Asistida**: PASS. Esta iteracion modifica
  HTML, CSS y JS en la pantalla `rompehielo`, por lo que el plan incluye
  validacion explicita de layout tablet portrait/landscape, estabilidad al
  rotar, estados `disabled` y feedback visible. Se deja documentado que el
  alcance aprobado de esta iteracion es solo tablet/escritorio, sin soporte
  formal para movil `360-767px`.
- **Impacto Visual y Funcional sobre Patrones Internos**: PASS. Se reutiliza la
  ruta existente, el template Django actual y los static assets de `etapasJuego`
  para mejorar la experiencia visible sin abrir una URL nueva. El nuevo servicio
  `services/roulette.py` se justifica como encapsulacion de dominio y no bloquea
  el trabajo UI.
- **No Regresion Verificada**: PASS. La validacion cubrira render HTML de
  `rompehielo`, bootstrap JSON con `?format=json`, temporizador existente,
  overlay de tiempo agotado hacia `etapa1`, integracion de mensajes de turno,
  rotacion en tablet y comportamiento del engine (`get_questions`,
  `select_question`, `handle_error`) sin tocar modelos, coevaluacion u OpenAI.
- **Evolucion Guiada por Demostracion**: PASS. La desviacion relevante no es
  solo agregar JSON, sino reestructurar la UI de `rompehielo` en los archivos
  existentes para elevar claramente la percepcion del jurado. El riesgo sigue
  siendo acotado porque no cambia contratos persistidos ni dependencias.
- **Usabilidad Funcional y Sin Friccion**: PASS. El plan contempla estado JS
  para seleccion de preguntas sin repeticion por ciclo, bloqueo temporal del
  boton, feedback en menos de `300ms`, mensajes accionables en la misma pantalla
  y continuidad hacia el siguiente turno o `etapa1`.
- **Higiene de Codigo**: PASS. Archivos inspeccionados antes de proponer cambios:
  `proyecIngSoft/etapasJuego/services/scoring.py`,
  `proyecIngSoft/etapasJuego/services/pitch_ai.py`,
  `proyecIngSoft/etapasJuego/services/__init__.py`,
  `proyecIngSoft/etapasJuego/views.py`,
  `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`,
  `proyecIngSoft/etapasJuego/static/etapasJuego/css/rompehielo.css`,
  `proyecIngSoft/etapasJuego/static/etapasJuego/js/rompehielo.js`,
  `proyecIngSoft/etapasJuego/urls.py`,
  `proyecIngSoft/etapasJuego/tests.py`.
  Se justifica `services/roulette.py` porque la responsabilidad no encaja en los
  servicios existentes y la constitucion exige no sobrecargar archivos ajenos
  sin afinidad de dominio. HTML, CSS y JS nuevos se concentran en los archivos
  existentes de `rompehielo` y se eliminara la logica placeholder reemplazada
  en el mismo cambio. No habra migraciones en esta iteracion.

## Project Structure

### Documentation (this feature)

```text
specs/001-rompehielo-ruleta/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── rompehielo-json.md
└── tasks.md
```

### Source Code (repository root)

```text
proyecIngSoft/
├── manage.py
├── proyecIngSoft/
│   └── urls.py
└── etapasJuego/
    ├── tests.py
    ├── urls.py
    ├── views.py
    ├── templates/
    │   └── etapasJuego/
    │       └── rompehielo.html
    ├── static/
    │   └── etapasJuego/
    │       ├── css/
    │       │   └── rompehielo.css
    │       └── js/
    │           └── rompehielo.js
    └── services/
        ├── __init__.py
        ├── pitch_ai.py
        ├── scoring.py
        └── roulette.py
```

**Structure Decision**: Se mantiene la estructura real de una app Django
modular. La nueva logica de dominio vive en `etapasJuego/services/roulette.py`;
la integracion HTTP se hace en `etapasJuego/views.py`; la experiencia visible se
implementa sobre `templates/etapasJuego/rompehielo.html` y sus assets
`static/etapasJuego/css/rompehielo.css` y
`static/etapasJuego/js/rompehielo.js`; la ruta existente se conserva en
`etapasJuego/urls.py`; y las pruebas se agregan en `etapasJuego/tests.py` para
seguir el patron actual del proyecto.

## Phase 0: Research

Resultados consolidados en [research.md](./research.md):

1. Mantener un engine stateless con catalogo en memoria e interfaz estable para
   futura migracion a modelo Django.
2. Reutilizar la URL existente `/etapasJuego/tablet/rompehielo/` y habilitar
   modo JSON por query param o header de aceptacion en vez de crear otra URL.
3. Reestructurar la UI existente de `rompehielo` en los archivos actuales
   `rompehielo.html`, `rompehielo.css` y `rompehielo.js` en vez de crear una
   nueva pantalla, para mantener continuidad y cumplir la higiene de codigo.
4. El desarrollador confirma que `rompehielo` se valida solo para tablet y
   escritorio en esta iteracion; movil `360-767px` queda fuera del alcance
   formal de aprobacion.
5. Probar engine, vista y estados base del flujo con `django.test.TestCase` en
   el modulo existente, complementado por verificacion manual tablet-first.

## Phase 1: Design

### Data Model

Definido en [data-model.md](./data-model.md). El diseno separa:

- Catalogo de preguntas consumido por `RouletteEngine`
- Subconjunto `available_ids` administrado por el cliente
- Respuesta de error serializable para la vista AJAX

### Contracts

Definidos en [contracts/rompehielo-json.md](./contracts/rompehielo-json.md).
El contrato documenta la misma URL en dos modos:

- `GET /etapasJuego/tablet/rompehielo/` -> HTML
- `GET /etapasJuego/tablet/rompehielo/?format=json` -> JSON

### Quickstart

Definido en [quickstart.md](./quickstart.md) con pasos de implementacion y
verificacion manual/local.

## Implementation Strategy

1. Crear `proyecIngSoft/etapasJuego/services/roulette.py` con una clase
   `RouletteEngine` que encapsule un catalogo en memoria y una interfaz publica
   estable (`get_questions`, `select_question`, `handle_error`).
2. Exportar `RouletteEngine` desde `proyecIngSoft/etapasJuego/services/__init__.py`
   solo si el modulo ya se usa como fachada del paquete.
3. Actualizar `proyecIngSoft/etapasJuego/views.py` para que `rompehielo`
   detecte modo JSON por `?format=json` o encabezado `Accept:
   application/json`, devolviendo `JsonResponse` con la lista completa y
   manteniendo el render del template cuando no se solicite JSON.
4. Rehacer `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`
   para incluir ruleta central, area principal de pregunta, mensaje para
   responder, mensaje para pasar la tablet y continuidad hacia `etapa1`.
5. Actualizar `proyecIngSoft/etapasJuego/static/etapasJuego/css/rompehielo.css`
   para sostener layout tablet-first, jerarquia visual, estados `disabled` y
   estabilidad de contenido dinamico sin overflow.
6. Actualizar `proyecIngSoft/etapasJuego/static/etapasJuego/js/rompehielo.js`
   para manejar bootstrap de preguntas, seleccion sin repeticion por ciclo,
   bloqueo temporal del boton principal, feedback visible y mensajes de error o
   reintento dentro de la misma pantalla.
7. Validar la pantalla como flujo de tablet/escritorio; movil `360-767px` queda
   explicitamente fuera del alcance formal de esta iteracion.
8. Agregar pruebas en `proyecIngSoft/etapasJuego/tests.py` para engine y vista,
   complementadas con validacion manual de la experiencia visual y responsive.

## File Ownership

- **Modificar**:
  `proyecIngSoft/etapasJuego/views.py`,
  `proyecIngSoft/etapasJuego/tests.py`,
  `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`,
  `proyecIngSoft/etapasJuego/static/etapasJuego/css/rompehielo.css`,
  `proyecIngSoft/etapasJuego/static/etapasJuego/js/rompehielo.js`,
  `proyecIngSoft/etapasJuego/services/__init__.py` (si aplica),
  `specs/001-rompehielo-ruleta/plan.md`
- **Crear**:
  `proyecIngSoft/etapasJuego/services/roulette.py`,
  `specs/001-rompehielo-ruleta/research.md`,
  `specs/001-rompehielo-ruleta/data-model.md`,
  `specs/001-rompehielo-ruleta/quickstart.md`,
  `specs/001-rompehielo-ruleta/contracts/rompehielo-json.md`
- **Eliminar**: Ninguno previsto

## Post-Design Constitution Check

- **Percepcion del Cliente/Jurado como Criterio Final**: PASS. El diseno final
  queda orientado a una mejora perceptible de la demo, no a un cambio interno
  invisible: ruleta clara, mensajes guiados y flujo de turno mas ordenado.
- **Identidad Inmersiva y Experiencia Asistida**: PASS. El plan ya reconoce la
  modificacion de HTML/CSS/JS y exige validar estados visuales, orientacion,
  lectura a distancia y tablet portrait/landscape. La decision de alcance queda
  cerrada: esta iteracion se aprueba solo para tablet/escritorio.
- **Impacto Visual y Funcional sobre Patrones Internos**: PASS. La experiencia
  visible mejora sobre los archivos existentes del modulo, mientras el servicio
  nuevo encapsula solo la parte de dominio compartible.
- **No Regresion Verificada**: PASS. La validacion contempla HTML, JSON,
  temporizador, overlay de salida, continuidad de la ruta y comportamiento de
  engine sin alterar modelos ni contratos persistidos.
- **Evolucion Guiada por Demostracion**: PASS. La desviacion principal se
  limita a rehacer la pantalla existente en sus archivos reales, con riesgo
  acotado y evidencia de validacion prevista.
- **Usabilidad Funcional y Sin Friccion**: PASS. El diseno incluye una sola
  accion primaria dominante, feedback visible, reintento en la misma pantalla y
  continuidad de flujo sin callejones sin salida.
- **Higiene de Codigo**: PASS. Se crea un unico archivo nuevo justificado por
  dominio (`services/roulette.py`) y el resto del trabajo se concentra en los
  archivos existentes de `rompehielo`, sin planificar archivos redundantes.

## Complexity Tracking

No se anticipan violaciones constitucionales que requieran justificacion.
