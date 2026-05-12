# Misión Emprende — Transformación a Frontend-Only

## Descripción del Proyecto Original

**Misión Emprende** es una plataforma gamificada de emprendimiento educativo implementada en Django 5.x. Los estudiantes pasan por 4 etapas cronometradas:

1. **Etapa 1 — Sopa de Letras**: Juego colaborativo de búsqueda de palabras (vocabulario de emprendimiento)
2. **Etapa 2 — Selección de Desafío**: Los equipos eligen un desafío social de 3 temáticas (Salud, Sustentabilidad, Educación)
3. **Etapa 3 — Mapa de Empatía**: Design thinking con los 5 cuadrantes del usuario
4. **Etapa 4 — Pitch**: Propuesta de valor evaluada con inteligencia artificial (OpenAI)

La plataforma contaba además con paneles para **Administrador** y **Profesor** (gestión de secciones, sesiones, equipos, tablets, desafíos y evaluaciones).

---

## Objetivo de la Transformación

Convertir el proyecto a **frontend-only**: Django sirve las páginas HTML con sus estilos y scripts, pero sin lógica de base de datos en las vistas. Se preserva el diseño de base de datos MySQL en los `models.py` como documentación del esquema.

**El proyecto corre con:** `python manage.py runserver` (SQLite incluido, sin necesitar MySQL activo)

---

## Cambios Realizados

### Archivos Eliminados

| Archivo | Razón |
|---------|-------|
| `login/forms.py` | Formularios Django ligados a modelos (CRUD) |
| `etapasJuego/services/pitch_ai.py` | Integración OpenAI para evaluación de pitches |
| `etapasJuego/services/scoring.py` | Cálculo de tokens por equipo |
| `etapasJuego/services/roulette.py` | Motor de selección aleatoria de desafíos |
| `etapasJuego/wordsearch/engine.py` | Generador Python de tableros de sopa de letras |
| `login/templates/login/estudiante_ingresado.html` | Template de confirmación post-login (flujo eliminado) |

### Archivos Modificados

#### `login/views.py`
- Eliminada: autenticación Django (`authenticate`, `login`), queries de `Estudiante`, `GameSession`, `Team`, `Tablet`
- Reemplazado: `login_view` ahora acepta cualquier POST y redirige a `home_estudiante` (modo demo sin validación)
- Mantenido: `home_estudiante`, `logout_view`

#### `login/urls.py`
- Eliminada: URL `estudiante_ingresado/<int:estudiante_id>/` (flujo ya no existe)
- Mantenidas: `login`, `home_estudiante`, `logout`

#### `login/panel_views.py`
- Eliminados: todos los imports de modelos, formularios y servicios
- Eliminados: decoradores `@admin_required` / `@profesor_required` (paneles accesibles sin autenticación)
- Reemplazadas: todas las ~30 vistas con renders simples que pasan listas vacías `[]` como contexto
- Efecto: los paneles de Admin y Profesor cargan visualmente pero sin datos reales

#### `etapasJuego/views.py`
- Eliminados: imports de `wordsearch.engine`, `services`, `context`, `models` de DB
- Reemplazadas: todas las vistas de juego con renders simples usando datos hardcodeados
- Añadidos: datos de demostración (`DEMO_SQUAD_TOPICS`, `DEMO_WORDS`, `DEMO_TIPS`)
- Añadidas: APIs mock para `wordsearch.js` (retornan JSON estático sin consultar DB)

#### `etapasJuego/services/__init__.py`
- Eliminado: import de `RouletteEngine` (el archivo fue eliminado)

#### `etapasJuego/models.py`
- Modificado: método `Team.update_tokens()` convertido a stub vacío (ya no llama a `scoring.py`)

#### `etapaFinal/views.py`
- Eliminados: imports de `context`, `Evaluation`, `Team`, `Project`
- Reemplazadas: 4 vistas con renders simples y un JSON mock para `save_coevaluacion`

#### `proyecIngSoft/settings.py`
- Eliminada: línea `OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")`

---

## Flujo de Navegación Frontend

```
/ → /login/
/login/ → formulario (cualquier POST acepta)
/login/ [POST] → /login/home_estudiante/

/login/home_estudiante/
  → Pantalla "Misión Emprende" con personajes y botón "Iniciar ruta"
  → Botón: /etapasJuego/tablet/seleccion-modalidad/

/etapasJuego/tablet/seleccion-modalidad/
  → /etapasJuego/tablet/rompehielo/

/etapasJuego/tablet/rompehielo/
  → /etapasJuego/etapa/1/ (sopa de letras)

/etapasJuego/etapa/1/
  → Tablero 10×10 generado aleatoriamente
  → Al acabar el tiempo: /etapasJuego/etapa/1/ranking/

/etapasJuego/etapa/1/ranking/
  → /etapasJuego/inicio-historia/

/etapasJuego/inicio-historia/
  → 3 escuadrones hardcodeados (Salud/Rojo, Sustentabilidad/Azul, Educación/Amarillo)
  → Selección → modal con 3 desafíos por escuadrón
  → Submit → /etapasJuego/etapa/2/seleccion/

/etapasJuego/etapa/2/seleccion/
  → Mapa de empatía (5 burbujas)
  → /etapasJuego/etapa/3/

/etapasJuego/etapa/3/
  → Carga de foto de prototipo
  → /etapasJuego/etapa/4/

/etapasJuego/etapa/4/
  → Pitch con tips hardcodeados
  → /etapa-final/

/etapa-final/
  → Coevaluación (lista vacía)
  → /etapa-final/final/

/etapa-final/final/
  → Ranking final (vacío en modo demo)
```

---

## Paneles de Administración

Accesibles en:
- **Admin**: `/admin-panel/` → `/admin-panel/secciones/`, `/admin-panel/sesiones/`, `/admin-panel/topics/`, etc.
- **Profesor**: `/profesor/` → `/profesor/sesiones/`, `/profesor/alumnos/`, `/profesor/equipos/`, etc.

Las páginas cargan con tablas vacías. Sin datos reales porque no hay queries a la base de datos.

---

## Cómo Ejecutar el Proyecto

```bash
# 1. Activar entorno virtual
source proyecIngSoft/.venv_local/bin/activate

# 2. Ir al directorio del proyecto
cd proyecIngSoft

# 3. Correr el servidor
python manage.py runserver

# 4. Abrir en el navegador
# http://127.0.0.1:8000/
```

No se requiere configurar MySQL ni OpenAI para que el proyecto funcione.

---

## Diseño de Base de Datos (Modelos Preservados)

Los `models.py` de todas las apps se conservan sin cambios como documentación del esquema MySQL.

### App: `login`

| Modelo | Descripción |
|--------|-------------|
| `Carrera` | Catálogo de carreras universitarias |
| `SeccionEstudiantes` | Secciones de curso (carrera + año ingreso) |
| `Estudiante` | Estudiante registrado, vinculado a sección y equipo |

### App: `etapasJuego`

| Modelo | Descripción |
|--------|-------------|
| `GameSession` | Sesión de juego de una sección (configuración de tiempos, URLs QR, modo asignación) |
| `Team` | Equipo de estudiantes con tokens (empatía, creatividad, evaluación) |
| `Tablet` | Dispositivo asignado a un equipo con PIN de acceso |
| `TeamGameSession` | Estado de la sopa de letras por equipo (tablero JSON, palabras encontradas, progreso) |
| `Topic` | Temática de desafíos (Salud, Sustentabilidad, Educación) |
| `Challenge` | Desafío principal vinculado a un Topic, con video opcional |
| `Desafio` | Caso específico dentro de un Challenge (historia, personaje, imagen) |
| `Project` | Proyecto del equipo (desafío seleccionado, foto prototipo, resumen idea) |
| `EmpathyMap` | Mapa de empatía del equipo (gustos, miedos, problemas, contexto, hobbies) |
| `Pitch` | Pitch del equipo con guión, sugerencias IA y score automático |
| `Evaluation` | Coevaluación entre equipos (puntajes de empatía, creatividad, comunicación) |

### App: `etapaFinal`

Modelos de evaluación final (ver `etapaFinal/models.py`).

---

## Estructura de Archivos Resultante

```
proyecIngSoft/
├── manage.py
├── db.sqlite3
├── proyecIngSoft/
│   ├── settings.py          # Sin OPENAI_API_KEY
│   └── urls.py              # Sin cambios
├── login/
│   ├── models.py            # SIN CAMBIOS (diseño BD)
│   ├── views.py             # 3 vistas simples
│   ├── urls.py              # 3 rutas
│   ├── panel_views.py       # ~30 vistas estáticas
│   ├── admin_urls.py        # SIN CAMBIOS
│   ├── profesor_urls.py     # SIN CAMBIOS
│   └── templates/login/
│       ├── login.html
│       ├── home_estudiante.html
│       ├── admin/           (plantillas del panel admin)
│       └── profesor/        (plantillas del panel profesor)
├── etapasJuego/
│   ├── models.py            # update_tokens() → stub vacío
│   ├── views.py             # Vistas mock + APIs JSON estáticas
│   ├── urls.py              # SIN CAMBIOS
│   ├── services/
│   │   └── __init__.py      # Vacío
│   ├── wordsearch/
│   │   └── wordsearch.js    # SIN CAMBIOS (motor JS)
│   ├── static/etapasJuego/  # CSS y JS sin cambios
│   └── templates/etapasJuego/
├── etapaFinal/
│   ├── models.py            # SIN CAMBIOS
│   ├── views.py             # 4 vistas mock
│   └── templates/etapaFinal/
├── media/
│   ├── imgHistoria/         # Imágenes de escuadrones y villano
│   └── personajesPortada/   # Personajes de home_estudiante
└── static/                  # Archivos estáticos globales
```

---

## Comportamiento Esperado en Demo

| Funcionalidad | Estado |
|---------------|--------|
| Login (cualquier usuario) | ✅ Redirige a home |
| home_estudiante.html | ✅ Carga con animaciones |
| inicioHistoria.html | ✅ Muestra 3 escuadrones hardcodeados |
| Sopa de letras (tablero) | ✅ Tablero aleatorio visible, cronómetro activo |
| Sopa de letras (encontrar palabras) | ⚠️ Las palabras no se marcan como encontradas (API mock) |
| Mapa de empatía, Pitch, Prototipo | ✅ Formularios cargables (sin persistencia) |
| Coevaluación y ranking final | ✅ Páginas vacías |
| Paneles Admin / Profesor | ✅ Tablas vacías, navegación funcional |
| Video de bienvenida | ⚠️ Requiere archivo `static/videos/bienvenida.mp4` |
