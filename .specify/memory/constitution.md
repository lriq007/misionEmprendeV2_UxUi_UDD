<!--
Sync Impact Report
Version change: 2.2.0 -> 2.3.0
Modified principles:
- II. Identidad Inmersiva y Experiencia Asistida (expanded mobile and tablet real-use requirements)
Added sections:
- None
Removed sections:
- None
Templates requiring updates:
- updated: .specify/templates/plan-template.md
- updated: .specify/templates/spec-template.md
- updated: .specify/templates/tasks-template.md
- not present: .specify/templates/commands/*.md
Runtime guidance reviewed:
- updated: README.md
- reviewed: AGENTS.md
Follow-up TODOs:
- None
-->
# Mision Emprende Constitution

## Core Principles

### I. Percepcion del Cliente/Jurado como Criterio Final
Durante esta fase de desarrollo, la aprobacion final MUST depender estrictamente
de la percepcion y satisfaccion del cliente/jurado. Toda especificacion, plan,
tarea, revision y validacion MUST priorizar el resultado demostrable para ese
evaluador: claridad visual, impacto de la experiencia, facilidad de uso,
coherencia narrativa, fluidez funcional y confianza durante la demo. Una
decision que sea tecnicamente correcta pero reduzca la percepcion de calidad del
cliente/jurado no cumple esta constitucion.

Rationale: el proyecto sera evaluado por la experiencia percibida y por la
capacidad de demostrar valor, no por la fidelidad interna a patrones invisibles.

### II. Identidad Inmersiva y Experiencia Asistida
Toda pantalla nueva o modificada visible para estudiantes, profesores,
administradores o jurado MUST mantener o elevar la calidad visual y de
interaccion definida por `home_estudiante.html` y `seleccion_modalidad.html`.
Cada flujo MUST tener navegacion clara, acciones primarias identificables, foco
de teclado visible, estados `hover`/`active`/`disabled` cuando apliquen, ayuda
contextual y comportamiento responsivo probado para movil y tablet como
dispositivos de uso real, ademas de escritorio. Los breakpoints obligatorios son
movil `360-767px`, tablet portrait `768-1023px`, tablet landscape `1024-1279px`
y escritorio `1280px+`. En tablet, todo objetivo tactil interactivo MUST medir
al menos `44x44px`. Los flujos que sean consumidos en celular MUST
identificarse en su especificacion y probarse en viewport movil antes de
aprobarse. Los flujos criticos de juego MUST probarse en tablet portrait y
tablet landscape. El layout MUST mantenerse estable al rotar el dispositivo
durante una sesion activa. Cuando una pantalla no haya sido identificada
previamente como responsiva para movil, la consulta de que interfaces aplican
responsividad movil MUST hacerse al desarrollador antes de planificar o
implementar el cambio. El contenido MUST NOT desbordar su contenedor ni ocultar
controles criticos en pantallas pequenas.

Rationale: la plataforma debe sentirse como una mision guiada, ludica y
confiable; la orientacion inmediata y la estabilidad visual son parte del
producto evaluado.

### III. Impacto Visual y Funcional sobre Patrones Internos
Cualquier decision tecnica que mejore significativamente la percepcion visual o
funcional del cliente/jurado MUST tener prioridad absoluta sobre la conservacion
de patrones internos de arquitectura, organizacion de codigo o estilo heredado,
siempre que el cambio demuestre que no rompe el sistema existente. Los patrones
Django actuales (`login`, `etapasJuego`, `etapaFinal`, URLs por app, templates
server-rendered, static/media, migraciones y `.env`) SHOULD reutilizarse cuando
ayuden a entregar rapido y sin regresiones, pero MUST NOT bloquear una mejora
visible o funcional superior.

Rationale: la arquitectura existe para sostener la experiencia. Cuando un
patron interno limita una mejora importante para la demo, el patron cede ante la
mejora verificada.

### IV. No Regresion Verificada
Todo cambio que priorice impacto visual o funcional MUST incluir una validacion
explicita de no regresion antes de considerarse aprobado. La validacion MUST
cubrir las rutas, templates, formularios, sesiones de juego, timers, asignacion
de equipos, tablets, coevaluacion, resultados finales, datos y uso de OpenAI que
puedan verse afectados. Los cambios de modelos MUST incluir migraciones Django y
preservar compatibilidad con datos existentes o documentar una migracion segura.

Rationale: priorizar la percepcion del cliente/jurado no autoriza romper flujos
existentes; la mejora debe ser visible y segura al mismo tiempo.

### V. Evolucion Guiada por Demostracion
Cada desviacion relevante de patrones internos MUST documentar el beneficio
esperado para el cliente/jurado y la evidencia de que el sistema sigue
funcionando. La autorizacion explicita del desarrollador es REQUIRED solo cuando
la desviacion incremente riesgo de regresion, cambie contratos de datos, agregue
dependencias significativas o altere flujos existentes. Las mejoras visuales o
funcionales de bajo riesgo que eleven claramente la demo MAY implementarse sin
detener el trabajo, siempre que se validen y queden trazables.

Rationale: la gobernanza debe acelerar mejoras perceptibles y reservar las
pausas de autorizacion para decisiones con riesgo real.

### VI. Usabilidad Funcional y Sin Friccion
Toda accion del usuario MUST producir feedback visible en menos de `300ms`,
incluyendo carga, confirmacion, deshabilitacion temporal, error o cambio de
estado. Todo flujo MUST ofrecer una ruta clara hacia adelante y hacia atras, sin
callejones sin salida. Los errores MUST ser accionables: deben describir que
paso y que hacer a continuacion. Acciones similares MUST comportarse igual en
todas las pantallas. Cada pantalla MUST tener una sola accion primaria
dominante. Cada pantalla MUST presentar como maximo tres decisiones simultaneas;
si una pantalla exige mas, el flujo MUST redisenarse o dividirse.

Rationale: la demo debe sentirse guiada, inmediata y recuperable. La friccion
funcional reduce confianza aunque la interfaz sea visualmente atractiva.

## Estandares Tecnicos y de Interfaz

- Frontend MUST usar templates Django y static assets coherentes con la app
  correspondiente cuando eso no limite una mejora visual o funcional superior.
- Nuevas pantallas de juego o seleccion MUST reutilizar o extender los patrones
  visuales de `mission-ui`, logos, paneles, ayudas, botones y estados activos
  existentes, salvo que una alternativa mejore claramente la percepcion del
  cliente/jurado y demuestre no regresion.
- CSS nuevo MUST contemplar responsividad, foco visible y estabilidad de layout
  para textos dinamicos, tarjetas, botones, overlays y controles interactivos.
- CSS nuevo o modificado MUST cubrir movil y tablet como dispositivos de uso
  real mediante los breakpoints `360-767px`, `768-1023px`, `1024-1279px` y
  `1280px+`, con objetivos tactiles de al menos `44x44px` en tablet.
- Flujos consumidos en celular MUST identificarse en la especificacion y
  probarse en viewport movil antes de aprobarse.
- Cambios responsivos en pantallas no identificadas previamente MUST consultar
  al desarrollador que interfaces aplican responsividad movil antes de
  planificar o implementar.
- Flujos criticos de juego MUST validar tablet portrait, tablet landscape y
  rotacion de dispositivo durante sesion activa sin perdida de estado ni saltos
  de layout que oculten acciones.
- Interacciones de usuario MUST mostrar feedback visible en menos de `300ms` y
  mantener consistencia de comportamiento entre acciones equivalentes.
- Backend MUST mantener secretos fuera del repositorio y leerlos desde `.env` o
  configuracion equivalente.
- Modelos nuevos o cambios de modelos MUST incluir migraciones, `__str__` claro
  cuando aporte trazabilidad, relaciones con `related_name` cuando sean
  consumidas por vistas/templates, y reglas de validacion en el nivel adecuado.
- Integraciones externas, incluida OpenAI, MUST aislar errores, evitar exponer
  claves y conservar una ruta de fallo comprensible para usuarios o docentes.

### Higiene de Codigo

- Antes de crear un archivo nuevo, el agente MUST verificar si existe uno que
  cumpla la misma funcion y modificarlo en su lugar.
- Esta prohibido dejar funciones, vistas, templates, clases CSS o archivos sin
  ningun consumidor activo en el proyecto.
- Cada tarea de implementacion MUST declarar explicitamente que archivos
  modifica, cuales crea y cuales elimina. No se acepta "solo agrego" sin
  justificacion.
- Si una implementacion requiere reemplazar logica existente, el codigo anterior
  MUST eliminarse en el mismo cambio, no comentarse ni dejarse como respaldo.
- CSS y JS nuevos MUST agregarse en el archivo existente del componente o app
  correspondiente, no en archivos nuevos salvo que el volumen o la separacion de
  responsabilidades lo justifique explicitamente.
- Las migraciones Django generadas MUST revisarse antes de aplicarse para
  confirmar que no contienen operaciones redundantes o conflictivas con
  migraciones anteriores.

## Criterio de Priorizacion

Cuando existan alternativas tecnicas viables, el orden de decision MUST ser:

1. Mayor percepcion de calidad, claridad y satisfaccion para cliente/jurado.
2. No regresion demostrada del sistema existente.
3. Velocidad y confiabilidad para llegar a una demo funcional.
4. Coherencia con patrones internos de arquitectura y codigo.

Los patrones internos son una preferencia operativa, no un veto. Solo bloquean
una decision cuando la alternativa propuesta no mejora de forma significativa la
percepcion del cliente/jurado o no puede demostrar no regresion.

## Flujo de Desarrollo y Revision

- Cada plan MUST declarar como pasa los seis principios antes de iniciar
  investigacion o diseno, y MUST repetir la revision antes de generar tareas.
- Cada especificacion MUST incluir criterios de aceptacion que cubran UX/UI,
  responsividad por breakpoint, flujos consumidos en celular, tablet
  portrait/landscape, ayuda contextual, feedback visible, errores accionables,
  percepcion del cliente/jurado y no regresion cuando apliquen.
- Cada lista de tareas MUST incluir validacion de la experiencia visual y de los
  flujos Django afectados, ademas de pruebas o pasos manuales verificables para
  viewport movil, tablet portrait/landscape, rotacion, feedback en menos de
  `300ms`, rutas hacia adelante/atras y errores accionables cuando apliquen.
- Cada tarea de implementacion MUST declarar archivos modificados, creados y
  eliminados, y MUST justificar cualquier archivo nuevo frente a la posibilidad
  de modificar uno existente.
- Cualquier desviacion relevante de patrones internos MUST quedar documentada
  con su beneficio perceptible, riesgo, validacion y autorizacion cuando aplique.
- Los cambios SHOULD ser pequenos, trazables y ubicados en los archivos del
  dominio afectado cuando eso no bloquee una mejora demostrable; refactors
  amplios requieren justificacion y validacion adicional.

## Governance

Esta constitucion tiene prioridad sobre practicas informales, plantillas y
planes de implementacion. Las especificaciones, planes, tareas y revisiones MUST
verificar cumplimiento constitucional antes de aprobar trabajo.

Las enmiendas requieren:

1. Descripcion del cambio y del problema que resuelve.
2. Evaluacion de impacto sobre frontend, backend, datos, pruebas y documentacion.
3. Confirmacion de que mejora o preserva la percepcion del cliente/jurado.
4. Confirmacion de que no introduce regresiones en el sistema existente.
5. Actualizacion de plantillas y guias afectadas en el mismo cambio.

Versioning policy:

- MAJOR: redefinicion incompatible de principios, eliminacion de garantias base
  o cambio de gobierno.
- MINOR: nuevos principios, nuevas secciones obligatorias o ampliacion material
  de reglas existentes.
- PATCH: aclaraciones, ejemplos, correcciones editoriales o ajustes sin cambio
  semantico.

Compliance review:

- Planes MUST registrar el resultado del Constitution Check.
- PRs o cambios locales MUST declarar pruebas ejecutadas o validacion manual.
- Si se detecta incumplimiento, el trabajo se detiene hasta corregirlo o recibir
  autorizacion explicita para una mejora superior con no regresion demostrada.

**Version**: 2.3.0 | **Ratified**: 2026-04-20 | **Last Amended**: 2026-04-20
