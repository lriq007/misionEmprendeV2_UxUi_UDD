# Feature Specification: Actualizacion Rompehielo Ruleta

**Feature Branch**: `[001-rompehielo-ruleta]`  
**Created**: 2026-04-23  
**Status**: Draft  
**Input**: User description: "Modifica y actualiza la interfaz asociada a \"rompehielo.html\". Actualiza según los estilos especificados en la constitucion. Además se debe agregar um panel principal con un reluta y en el centro un boton de siguiente turno. Cada apartado de la ruleta es una pregunta para el usuario. Luego de salir seleccionada una pregunta se debe mostrar en pantalla en un lugar apropiado para tablet un mensaje que indique, comparte con tus compañeros la respuesta. Luego se actualiza el otro mensaje en otra posición especificando, entregale la tablet al siguiente compañero."

## Clarifications

### Session 2026-04-23

- Q: Como debe comportarse la seleccion de preguntas entre turnos consecutivos y al agotar la ruleta? → A: Seleccion aleatoria sin repeticion hasta agotar todas las preguntas; luego se reinicia la ruleta.
- Q: Como debe comportarse el boton de siguiente turno ante toques repetidos mientras el turno actual aun se resuelve? → A: Mientras se resuelve el turno actual, toques extra se ignoran y el boton muestra un estado deshabilitado o de carga breve.
- Q: Como debe responder la interfaz si falla la seleccion visual de una pregunta o la actualizacion del turno? → A: Mostrar error en la misma pantalla y habilitar reintento con el mismo boton principal.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Guiar un turno de rompehielo (Priority: P1)

Como grupo de estudiantes usando una tablet, queremos ver una ruleta central con
preguntas y un boton dominante para avanzar al siguiente turno, para que la
actividad de rompehielo sea clara, dinamica y facil de seguir sin explicacion
adicional.

**Why this priority**: La ruleta y el control de turno son el nucleo funcional
de la experiencia solicitada y determinan si la dinamica se puede ejecutar en
demo de manera fluida.

**Independent Test**: Puede probarse cargando la pantalla de rompehielo en una
tablet, activando varios turnos consecutivos y verificando que cada accion
entrega una pregunta visible y un camino claro para continuar.

**Acceptance Scenarios**:

1. **Given** que el grupo abre la pantalla de rompehielo, **When** la interfaz
   termina de cargar, **Then** se muestra un panel principal con ruleta
   visible, preguntas distribuidas en secciones y un boton central de
   "siguiente turno" como accion primaria dominante.
2. **Given** que la ruleta esta lista para usar, **When** el grupo activa el
   siguiente turno, **Then** la pantalla selecciona una pregunta de la ruleta y
   la muestra en un area principal legible para todos los participantes.
3. **Given** que una pregunta ya fue seleccionada, **When** termina la
   seleccion del turno, **Then** la interfaz mantiene disponible una forma clara
   de pasar al siguiente turno sin generar callejones sin salida.

---

### User Story 2 - Indicar la accion del participante actual (Priority: P2)

Como participante actual, quiero recibir una instruccion clara para compartir mi
respuesta con el grupo justo despues de que la ruleta seleccione una pregunta,
para saber que debo hacer sin depender del facilitador.

**Why this priority**: La actividad pierde ritmo si la pantalla no convierte la
pregunta en una consigna inmediata y visible.

**Independent Test**: Puede probarse ejecutando un turno y confirmando que,
despues de la seleccion, aparece el mensaje "comparte con tus compañeros la
respuesta" en una posicion visible y apropiada para tablet.

**Acceptance Scenarios**:

1. **Given** que la ruleta selecciona una pregunta, **When** la seleccion se
   confirma visualmente, **Then** la pantalla muestra un mensaje de apoyo que
   indica al participante compartir la respuesta con sus companeros.
2. **Given** que el mensaje de compartir esta visible, **When** el contenido
   dinamico se acomoda en tablet portrait o landscape, **Then** el mensaje se
   mantiene legible, sin tapar la pregunta ni el control principal.

---

### User Story 3 - Transferir la tablet al siguiente companero (Priority: P3)

Como grupo, queremos que la pantalla indique claramente cuando toca pasar la
tablet al siguiente companero, para evitar dudas sobre el cambio de turno y
mantener el flujo ordenado.

**Why this priority**: Esta instruccion complementa la dinamica del turno y
reduce friccion entre participantes, pero depende de que la pregunta ya haya
sido seleccionada y mostrada.

**Independent Test**: Puede probarse completando un turno y verificando que la
segunda indicacion aparece en una ubicacion distinta, claramente asociada al
siguiente paso del flujo.

**Acceptance Scenarios**:

1. **Given** que una pregunta fue mostrada al participante actual, **When** la
   interfaz actualiza las ayudas del turno, **Then** aparece un mensaje
   adicional que indica entregar la tablet al siguiente companero.
2. **Given** que ambas indicaciones estan visibles, **When** el usuario observa
   la pantalla a distancia tipica de mesa, **Then** puede distinguir cual
   mensaje corresponde a responder y cual corresponde al relevo del dispositivo.

---

### Edge Cases

- Que ocurre si el grupo presiona el boton de siguiente turno repetidamente en
  poco tiempo.
- Los toques repetidos mientras el turno actual aun se resuelve deben ignorarse
  y el boton principal debe mostrar un estado deshabilitado o de carga breve.
- La misma pregunta no debe volver a salir en turnos consecutivos dentro del
  mismo ciclo de preguntas; al agotarse la ruleta, el sistema reinicia el
  conjunto disponible y puede reutilizar preguntas en un nuevo ciclo.
- Como se presenta el contenido si una pregunta es mas larga que las demas y
  exige mas de una linea en tablet portrait.
- Como se preserva la visibilidad de la pregunta, los mensajes y la accion
  principal al rotar la tablet durante un turno activo.
- Que feedback visible aparece en menos de `300ms` despues de activar el
  siguiente turno.
- Como mantiene la pantalla una ruta clara para avanzar hacia el proximo turno y
  para salir hacia la etapa siguiente cuando termine el tiempo global del
  rompehielo.
- Si ocurre un error que impida actualizar la pregunta o el estado visual del
  turno, la pantalla debe informar el problema en contexto y permitir reintento
  inmediato con el mismo boton principal.
- Como se evita desborde, superposicion o perdida de legibilidad cuando los
  textos dinamicos conviven con el temporizador y otros paneles de apoyo.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST actualizar la interfaz de `rompehielo` para que
  siga la identidad visual, ayuda contextual, claridad de accion y calidad
  percibida exigidas por la constitucion del proyecto.
- **FR-002**: El sistema MUST mostrar un panel principal de rompehielo con una
  ruleta como elemento central de la dinamica.
- **FR-003**: El sistema MUST incluir un boton central de "siguiente turno"
  dentro del panel principal y tratarlo como la unica accion primaria dominante
  de la pantalla durante la dinamica.
- **FR-003a**: Mientras un turno este resolviendo la seleccion visual de la
  pregunta y la actualizacion de mensajes, el boton de "siguiente turno" MUST
  ignorar toques adicionales y exponer un estado deshabilitado o de carga breve
  hasta que la interfaz vuelva a quedar lista.
- **FR-004**: Cada segmento visible de la ruleta MUST corresponder a una
  pregunta de rompehielo disponible para el grupo.
- **FR-005**: Al activar un nuevo turno, el sistema MUST seleccionar una
  pregunta de la ruleta y mostrarla en una zona principal legible desde el uso
  real de tablet.
- **FR-005a**: La seleccion de preguntas MUST ser aleatoria sin repeticion
  hasta consumir todas las preguntas disponibles; una vez agotadas, el sistema
  MUST reiniciar el conjunto y continuar la dinamica sin bloquear nuevos
  turnos.
- **FR-006**: Despues de mostrar la pregunta seleccionada, el sistema MUST
  presentar el mensaje "Comparte con tus companeros la respuesta" en una
  posicion destacada que no compita con la pregunta ni con la accion principal.
- **FR-007**: Luego del mensaje de respuesta, el sistema MUST actualizar otra
  zona de la interfaz con la instruccion "Entregale la tablet al siguiente
  companero" para dejar claro el relevo de turno.
- **FR-008**: El sistema MUST diferenciar visualmente la pregunta seleccionada,
  la instruccion para responder y la instruccion para pasar la tablet, para que
  el grupo identifique el orden del flujo sin explicacion externa.
- **FR-009**: El sistema MUST mantener visible el temporizador del rompehielo y
  la salida hacia la etapa siguiente sin romper la nueva dinamica de turnos.
- **FR-010**: El sistema MUST dar feedback visible en menos de `300ms` cuando se
  active el siguiente turno, incluyendo al menos un cambio perceptible de
  estado, seleccion o mensaje.
- **FR-011**: El sistema MUST evitar desbordes, solapamientos y ocultamiento de
  controles criticos cuando la pantalla se use en tablet portrait `768-1023px`
  y tablet landscape `1024-1279px`.
- **FR-012**: El sistema MUST mantener estabilidad visual y continuidad del
  turno si la tablet rota durante una sesion activa.
- **FR-013**: El sistema MUST conservar una experiencia funcional coherente con
  el flujo actual del rompehielo, incluida la navegacion posterior al termino
  del tiempo.
- **FR-014**: El sistema MUST mostrar mensajes accionables si no puede
  completar la seleccion visual de una pregunta o la actualizacion del turno.
- **FR-014a**: Si falla la seleccion visual de una pregunta o la actualizacion
  del turno, el sistema MUST mantener al grupo en la misma pantalla, explicar
  el problema de forma accionable y permitir reintentar usando el mismo boton
  principal.
- **FR-UX**: Si user-facing UI is changed, the system MUST preserve the visual
  quality, interaction states, contextual help and responsive behavior expected
  from `home_estudiante.html` and `seleccion_modalidad.html`.
- **FR-RESPONSIVE**: If user-facing UI is changed, the system MUST treat mobile
  and tablet as real-use devices where applicable. It MUST support mobile
  `360-767px`, tablet portrait `768-1023px`, tablet landscape `1024-1279px` and
  desktop `1280px+`; tablet touch targets MUST be at least `44x44px`; flows
  consumed on mobile MUST be identified in this specification and tested in a
  mobile viewport before approval; critical game flows MUST remain stable across
  tablet rotation.
- **FR-FRICTION**: User actions MUST provide visible feedback in under `300ms`;
  every flow MUST provide clear forward and backward movement; errors MUST state
  what happened and what to do next; equivalent actions MUST behave consistently
  across screens; each screen MUST have one dominant primary action and no more
  than three simultaneous decisions.
- **FR-PERCEPTION**: The system MUST prioritize changes that significantly
  improve client/jury perception, provided no existing flow is broken.
- **FR-REGRESSION**: If backend behavior is changed, the system MUST protect
  existing Django app boundaries, URL/template/static conventions,
  model/migration flow, environment configuration and affected role paths from
  regression. Internal patterns MAY change when they materially improve the demo
  and pass no-regression validation.
- **FR-HYGIENE**: Before creating a file, the implementation MUST verify whether
  an existing file fulfills the same role and modify it instead when possible.
  The implementation MUST NOT leave unused functions, views, templates, CSS
  classes or files; replaced logic MUST be deleted in the same change, not
  commented out; new CSS or JS MUST go into the existing component or app file
  unless explicit responsibility or volume justification is documented; Django
  migrations MUST be reviewed before application for redundant or conflicting
  operations.

### Key Entities *(include if feature involves data)*

- **Pregunta de rompehielo**: Consigna breve que puede mostrarse como segmento
  de ruleta y como pregunta activa del turno.
- **Turno de participante**: Estado visible de la dinamica que conecta una
  pregunta seleccionada con la accion de responder y el relevo de la tablet.
- **Mensaje de apoyo**: Indicacion contextual mostrada en pantalla para guiar la
  accion actual del grupo sin ambiguedad.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los grupos puede iniciar un nuevo turno e identificar
  la pregunta seleccionada en menos de 5 segundos desde que observa la pantalla.
- **SC-002**: En validacion manual de demo, la accion principal de siguiente
  turno recibe feedback visible en menos de `300ms` en cada activacion.
- **SC-003**: En tablet portrait y tablet landscape, la pantalla puede
  completarse sin overflow horizontal y sin ocultar pregunta, mensajes ni
  controles criticos.
- **SC-004**: Al menos el 90% de los participantes de prueba entiende sin ayuda
  externa que debe responder primero y luego entregar la tablet al siguiente
  companero.
- **SC-005**: La rotacion de la tablet durante un turno activo no elimina la
  pregunta seleccionada ni deja inaccesible la accion principal.
- **SC-006**: El flujo de fin de tiempo del rompehielo sigue permitiendo avanzar
  a la etapa siguiente sin pasos adicionales ni confusion observable.
- **SC-UX**: La interfaz resultante es evaluada como consistente con la calidad
  visual y la ayuda contextual de las pantallas de referencia del proyecto.
- **SC-RESPONSIVE**: Los breakpoints `768-1023px`, `1024-1279px` y `1280px+`
  pasan validacion visual; si se habilita uso en movil `360-767px`, la pantalla
  mantiene legibilidad basica y sin overflow horizontal.
- **SC-FRICTION**: Cada paso del turno expone una accion siguiente evidente y
  los mensajes de error incluyen que ocurrio y que hacer a continuacion.
- **SC-REG**: La ruta actual de rompehielo y la transicion posterior a la etapa
  siguiente siguen funcionando despues del cambio.
- **SC-HYGIENE**: La implementacion final declara archivos modificados, creados
  y eliminados; no deja codigo o estilos reemplazados sin uso.
- **SC-JURY**: Un evaluador de demo puede comprender la dinamica de la pantalla
  al verla por primera vez y percibe la actividad como ordenada, guiada y
  visualmente intencional.

## Assumptions

- La pantalla `rompehielo` se consume principalmente en tablet compartida por el
  grupo, por lo que tablet portrait y landscape son los contextos criticos de
  validacion.
- La lista de preguntas del rompehielo puede reutilizar el contenido ya presente
  en la pantalla actual, aunque su presentacion cambie hacia una ruleta.
- La ruleta consume cada pregunta una sola vez por ciclo antes de reiniciar el
  conjunto disponible.
- El temporizador existente y la navegacion hacia la siguiente etapa se
  mantienen como parte del flujo esperado del rompehielo.
- El objetivo del cambio es mejorar la demo y la claridad del flujo sin agregar
  nuevos roles, permisos ni persistencia de datos.
- La experiencia en movil no es el flujo principal de uso para esta pantalla;
  aun asi, si se mantiene disponible, debe conservar legibilidad basica y no
  bloquear el uso.
