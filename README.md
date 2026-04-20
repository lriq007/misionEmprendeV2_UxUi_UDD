# Mision Emprende

Proyecto web desarrollado con Django para apoyar una experiencia educativa de emprendimiento. La plataforma permite gestionar usuarios, secciones, sesiones, tablets, desafios, etapas de juego, coevaluacion y resultados finales.

## Descripcion

Mision Emprende es una aplicacion orientada a actividades pedagogicas donde estudiantes participan en distintas etapas de un juego formativo. El sistema incluye flujos para estudiantes, profesores y administradores, ademas de integracion con OpenAI para apoyar la evaluacion de pitchs.

## Git Branching Strategy

La gestion de ramas del proyecto separa produccion, integracion, desarrollo de
features, correcciones criticas y estabilizacion de releases. Todo cambio debe
entrar por Pull Request y respetar la convencion definida para mantener un
historial claro y trazable.

### Estructura de ramas

| Rama | Proposito | Reglas de uso |
|------|-----------|---------------|
| `main` | Produccion solamente. | Nunca recibe commits directos. Todo cambio entra via Pull Request desde `develop` o `hotfix/*`. Cada merge debe etiquetarse con versionado semantico `vMAJOR.MINOR.PATCH`. |
| `develop` | Hub central de integracion. | Todas las features terminadas se integran aqui primero. Es la unica fuente para liberar cambios hacia `main`. |
| `feature/*` | Una rama por feature o tarea, por ejemplo `feature/google-auth`. | Siempre nace desde `develop` y siempre vuelve a `develop` mediante Pull Request. |
| `hotfix/*` | Correcciones criticas de produccion, por ejemplo `hotfix/cors-headers`. | Siempre nace desde `main` y debe fusionarse de vuelta tanto a `main` como a `develop`. |
| `release/*` | Rama opcional de estabilizacion antes de fusionar a `main`. | Solo permite bugfixes. No se agregan features nuevas. |

### Reglas obligatorias

- Nunca hacer commit directo en `main` ni en `develop`. Todo entra por Pull Request.
- Cada Pull Request requiere al menos una aprobacion antes de fusionarse.
- Los nombres de ramas deben seguir la convencion `feature/`, `hotfix/` o `release/` seguida de un nombre corto y descriptivo en kebab-case.
- Los commits deben seguir Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:` o `chore:`.
- Las ramas `feature/*` deben mantenerse actualizadas con `develop` usando rebase o merge para evitar conflictos grandes.
- Eliminar las ramas despues de fusionarlas.
- Nunca usar `git push --force` en `main` ni en `develop`. Solo se permite `--force-with-lease` en ramas personales `feature/*` cuando sea necesario.

### Flujo correcto de Pull Requests

- `feature/*` -> `develop`
- `develop` -> `main` para releases
- `hotfix/*` -> `main`
- `hotfix/*` -> `develop`

```text
                 feature/*
                     |
                     v
main <---------- develop ----------> release/*
 ^                  ^
 |                  |
 |                  |
hotfix/* -----------+
 |
 v
main

Flujos principales:
feature/* -> develop
develop -> main
hotfix/* -> main
hotfix/* -> develop
```

## Tecnologias principales

- Python 3.11
- Django 5.2.7
- SQLite
- WhiteNoise
- Gunicorn
- Docker y Docker Compose
- OpenAI API

## Estructura del proyecto

```text
.
├── README.md
├── .gitignore
└── proyecIngSoft/
    ├── manage.py
    ├── requirements.txt
    ├── Dockerfile
    ├── docker-compose.yml
    ├── .dockerignore
    ├── proyecIngSoft/
    │   ├── settings.py
    │   ├── urls.py
    │   ├── asgi.py
    │   └── wsgi.py
    ├── login/
    ├── etapasJuego/
    ├── etapaFinal/
    ├── static/
    └── media/
```

## Modulos principales

- `login`: autenticacion, ingreso de estudiantes y paneles de usuario.
- `etapasJuego`: logica principal de las etapas del juego.
- `etapaFinal`: coevaluacion, resultados finales y foto grupal.
- `proyecIngSoft`: configuracion global del proyecto Django.

## Gobernanza de desarrollo

La constitucion del proyecto esta en `.specify/memory/constitution.md`. En esta
fase, el criterio de aprobacion final es la percepcion y satisfaccion del
cliente/jurado. Las decisiones tecnicas que mejoren significativamente esa
percepcion visual o funcional tienen prioridad sobre patrones internos de
arquitectura o codigo, siempre que se valide que no rompen el sistema existente.
Toda pantalla nueva o modificada debe validar usabilidad sin friccion: feedback
visible en menos de 300ms, errores accionables, una sola accion primaria
dominante y rutas claras hacia adelante y hacia atras. La responsividad trata
movil y tablet como dispositivos de uso real: se valida por separado en movil,
tablet portrait, tablet landscape y escritorio; los flujos consumidos en celular
deben identificarse y probarse en viewport movil antes de aprobarse. Antes de
planificar o implementar responsividad movil en una pantalla no identificada
previamente, se debe consultar al desarrollador que interfaces aplican. Los
flujos criticos de juego deben probarse en ambas orientaciones de tablet y
mantener estabilidad al rotar durante una sesion activa.
La higiene de codigo tambien es obligatoria: antes de crear archivos nuevos se
deben revisar archivos existentes que puedan cumplir la misma funcion, eliminar
codigo reemplazado en el mismo cambio, evitar elementos sin consumidor activo y
revisar migraciones Django generadas antes de aplicarlas.

## Spec Kit: instalacion y uso rapido

Este repositorio ya esta inicializado con Spec Kit para trabajar con desarrollo
guiado por especificaciones. La configuracion local esta en `.specify/` y los
comandos para Codex estan disponibles como skills en `.agents/skills/`.

Spec Kit no reemplaza a Django ni a Docker. Su funcion es ordenar el trabajo de
desarrollo antes de modificar codigo: primero se define una especificacion,
luego un plan tecnico, despues tareas ejecutables y finalmente la implementacion.

### Requisitos tecnicos de Spec Kit

Para instalar o actualizar Spec Kit en una maquina de desarrollo necesitas:

- Python 3.11 o superior.
- Git.
- `uv`, recomendado para instalar herramientas Python desde GitHub.
- Un agente compatible. Este proyecto fue inicializado para Codex.
- Acceso a internet si vas a instalar o actualizar desde el repositorio oficial.

Verifica las herramientas base:

```bash
python --version
git --version
uv --version
```

Si no tienes `uv`, instalalo desde su documentacion oficial antes de continuar.

### Estado de Spec Kit en este proyecto

La inicializacion actual del repositorio indica:

```text
Integracion: codex
Version Spec Kit: 0.7.4.dev0
Scripts: sh
Branch numbering: sequential
Context file: AGENTS.md
```

Archivos y carpetas principales:

- `.specify/init-options.json`: opciones usadas al inicializar Spec Kit.
- `.specify/integration.json`: integracion activa y version registrada.
- `.specify/memory/constitution.md`: reglas de gobernanza del proyecto.
- `.specify/templates/`: plantillas para specs, planes, tareas y checklists.
- `.specify/scripts/bash/`: scripts auxiliares usados por el flujo.
- `.agents/skills/speckit-*`: comandos de Spec Kit disponibles para Codex.
- `specs/`: carpeta donde se crean las features; puede no existir hasta crear la primera especificacion.

### Instalar Spec Kit en una maquina nueva

Si solo vas a trabajar en este repositorio ya inicializado, normalmente no
necesitas ejecutar `specify init` otra vez. Instala la CLI para poder verificar,
diagnosticar o actualizar Spec Kit:

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

Verifica la instalacion:

```bash
specify version
specify check
```

Si quieres ejecutar Spec Kit sin instalarlo de forma persistente:

```bash
uvx --from git+https://github.com/github/spec-kit.git specify --help
```

### Inicializar Spec Kit en otro proyecto

Para un proyecto nuevo:

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init nombre-del-proyecto --ai codex --script sh
```

Para inicializarlo dentro de una carpeta existente:

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init --here --ai codex --script sh
```

En este repositorio no ejecutes esos comandos salvo que quieras reinstalar o
actualizar los archivos de Spec Kit. Si necesitas actualizar las plantillas y
comandos del proyecto, usa:

```bash
specify init --here --force --ai codex --script sh
```

Antes de actualizar, revisa cambios pendientes con:

```bash
git status
```

### Flujo de trabajo recomendado

Usa los comandos de Spec Kit desde Codex en este orden:

1. Crear una especificacion funcional:

```text
/speckit.specify Describe la feature, el problema que resuelve, los usuarios involucrados y las reglas de negocio.
```

Resultado esperado:

- Crea `specs/NNN-nombre-feature/spec.md`.
- Crea un checklist de calidad de requisitos.
- Registra la feature activa en `.specify/feature.json`.
- Si el hook Git esta activo, puede crear una rama `NNN-nombre-feature`.

2. Aclarar requisitos si la especificacion quedo ambigua:

```text
/speckit.clarify
```

Resultado esperado:

- Reduce o elimina marcadores `NEEDS CLARIFICATION`.
- Actualiza la especificacion antes de pasar al plan tecnico.

3. Crear el plan tecnico:

```text
/speckit.plan
```

Resultado esperado:

- Crea `plan.md` dentro de la carpeta de la feature.
- Genera artefactos como `research.md`, `data-model.md`, `quickstart.md` y, si aplica, `contracts/`.
- Actualiza `AGENTS.md` para que los agentes lean el plan actual.

4. Generar tareas implementables:

```text
/speckit.tasks
```

Resultado esperado:

- Crea `tasks.md` con tareas ordenadas por dependencia.
- Marca tareas paralelizables cuando corresponde.
- Deja claro que archivos o modulos se deben modificar.

5. Revisar consistencia antes de codificar:

```text
/speckit.analyze
```

Resultado esperado:

- Revisa coherencia entre `spec.md`, `plan.md` y `tasks.md`.
- Detecta contradicciones, omisiones o tareas sin cobertura.

6. Implementar:

```text
/speckit.implement
```

Resultado esperado:

- Lee `tasks.md` y ejecuta el plan por fases.
- Verifica checklists antes de avanzar.
- Modifica el codigo siguiendo la especificacion aprobada.

### Comandos Git incluidos

El proyecto tiene habilitada la extension Git de Spec Kit. Los comandos
disponibles son:

```text
/speckit.git.initialize
/speckit.git.feature
/speckit.git.validate
/speckit.git.remote
/speckit.git.commit
```

La numeracion configurada es secuencial, por lo que las features usan prefijos
como `001-`, `002-` y `003-`. La configuracion de la extension esta en:

```text
.specify/extensions/git/git-config.yml
```

### Buenas practicas usando Spec Kit en este repositorio

- No empieces por editar codigo si la feature cambia comportamiento importante; primero crea o actualiza una spec.
- Mantener `spec.md` enfocado en valor de usuario y reglas de negocio, sin detalles de Django, templates o SQL.
- Documenta decisiones tecnicas en `plan.md`, no en la especificacion funcional.
- Usa `tasks.md` como contrato de implementacion: cada tarea debe ser concreta, verificable y estar asociada a archivos o modulos.
- Antes de implementar cambios visuales, respeta la constitucion del proyecto en `.specify/memory/constitution.md`.
- Antes de correr `/speckit.implement`, revisa que los checklists de la feature no tengan items pendientes.
- No subas secretos, bases SQLite locales ni entornos virtuales generados durante el trabajo.

### Solucion de problemas frecuentes

Si Codex no reconoce los comandos `/speckit.*`, revisa que existan los skills:

```bash
find .agents/skills -maxdepth 2 -name 'SKILL.md' | sort
```

Si Spec Kit no detecta la feature activa, revisa:

```bash
cat .specify/feature.json
git branch --show-current
```

Si el plan falla porque no encuentra una especificacion, primero ejecuta
`/speckit.specify` o confirma que exista una carpeta `specs/NNN-nombre-feature/`
con `spec.md`.

Si los scripts no se pueden ejecutar en Linux o macOS, asigna permisos:

```bash
chmod +x .specify/scripts/bash/*.sh
```

Si actualizaste Spec Kit y aparecen diferencias inesperadas, revisa el detalle
antes de continuar:

```bash
git diff -- .specify .agents AGENTS.md
```

## Requisitos previos

Para ejecutar el proyecto localmente necesitas tener instalado:

- Python 3.11 o superior
- pip
- Git

Opcionalmente, para ejecutar con contenedores:

- Docker
- Docker Compose

## Configuracion de variables de entorno

El proyecto utiliza un archivo `.env` dentro de la carpeta `proyecIngSoft/`.

Crea el archivo a partir del ejemplo:

```bash
cp proyecIngSoft/.env.example proyecIngSoft/.env
```

Luego edita `proyecIngSoft/.env` y agrega tus valores:

```env
OPENAI_API_KEY=tu_api_key_aqui
```

El archivo `.env` no debe subirse al repositorio porque puede contener claves privadas.

## Instalacion local

Desde la raiz del repositorio, entra a la carpeta del proyecto Django:

```bash
cd proyecIngSoft
```

Crea un entorno virtual:

```bash
python -m venv .venv
```

Activa el entorno virtual.

En Linux o macOS:

```bash
source .venv/bin/activate
```

En Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

Aplica las migraciones:

```bash
python manage.py migrate
```

Opcionalmente, crea un superusuario para acceder al administrador de Django:

```bash
python manage.py createsuperuser
```

Ejecuta el servidor de desarrollo:

```bash
python manage.py runserver
```

La aplicacion quedara disponible en:

```text
http://127.0.0.1:8000/
```

## Ejecucion con Docker

Docker permite ejecutar el proyecto sin activar un entorno virtual local. Las dependencias de Python se instalan dentro de la imagen usando `requirements.txt`.

Primero, asegúrate de tener instalado:

- Docker
- Docker Compose

Todos los comandos Docker se ejecutan desde la carpeta donde están `Dockerfile` y `docker-compose.yml`:

```bash
cd proyecIngSoft
```

Si no existe el archivo `.env`, créalo desde el ejemplo:

```bash
cp .env.example .env
```

Edita `.env` si necesitas configurar la API key de OpenAI:

```env
OPENAI_API_KEY=tu_api_key_aqui
```

Para construir la imagen:

```bash
docker compose build
```

Antes de levantar el proyecto por primera vez, aplica migraciones:

```bash
docker compose run --rm web python manage.py migrate
```

Recolecta archivos estáticos:

```bash
docker compose run --rm web python manage.py collectstatic --noinput
```

Opcionalmente, crea un superusuario para entrar al administrador de Django:

```bash
docker compose run --rm web python manage.py createsuperuser
```

Si necesitas cambiar la contraseña de un superusuario ya creado:

```bash
docker compose run --rm web python manage.py changepassword nombre_usuario
```

Para levantar la aplicación en primer plano:

```bash
docker compose up
```

Tambien puedes construir y levantar en un solo paso:

```bash
docker compose up --build
```

La aplicación quedará disponible en:

```text
http://127.0.0.1:8000/
```

Para detener la aplicación cuando está corriendo en primer plano, presiona `Ctrl + C`.

Para levantarla en segundo plano:

```bash
docker compose up -d
```

Para ver el estado de los servicios:

```bash
docker compose ps
```

Para ver logs:

```bash
docker compose logs -f web
```

Para apagar y limpiar los contenedores del proyecto:

```bash
docker compose down
```

El archivo `docker-compose.yml` monta la carpeta local dentro del contenedor con `.:/app`. Por eso, durante desarrollo, los cambios del código se reflejan dentro del contenedor y la base SQLite local `db.sqlite3` se conserva en tu máquina.

El archivo `.dockerignore` evita copiar a la imagen archivos que no son necesarios, como entornos virtuales, cachés, secretos locales, bases SQLite locales y `staticfiles/`. No reemplaza a `.gitignore`: `.gitignore` controla qué se sube a Git, mientras que `.dockerignore` controla qué entra al contexto de construcción Docker.

## Rutas principales

- `/`: redirige al login.
- `/login/`: ingreso de usuarios.
- `/admin/`: administrador nativo de Django.
- `/admin-panel/`: panel administrativo personalizado.
- `/profesor/`: panel de profesor.
- `/etapasJuego/`: inicio y flujo de etapas del juego.
- `/etapa-final/`: coevaluacion y resultados finales.

## Como iniciar el home de estudiante

Para poder llegar a `home_estudiante.html`, primero debe existir informacion minima en la base de datos. El flujo recomendado es crear un superusuario, entrar a Django Admin y registrar una seccion, una sesion de juego, una tablet y un equipo.

1. Crea la base de datos y un superusuario:

```bash
cd proyecIngSoft
python manage.py migrate
python manage.py createsuperuser
```

2. Levanta el servidor:

```bash
python manage.py runserver
```

3. Entra al administrador de Django:

```text
http://127.0.0.1:8000/admin/
```

4. En Django Admin, crea una `SeccionEstudiantes`.

Ejemplo:

```text
Nombre: INF-101
Carrera: Ingenieria en Informatica
Anio ingreso: 2025
```

5. Crea una `GameSession` asociada a esa seccion.

Ejemplo:

```text
Nombre: Sesion INF-101
Codigo: INF101
Seccion: INF-101
Modo asignacion: LOGIN_RANDOM
```

6. Crea una `Tablet` asociada a esa `GameSession`.

Ejemplo:

```text
Codigo: Tablet A
Descripcion: Tablet del equipo A
Sesion: Sesion INF-101
```

Al guardar la tablet, Django genera automaticamente un `codigo_acceso` de 4 digitos. Ese PIN es el que se usa en el login como tipo de usuario `Tableta`.

7. Crea un `Team` asociado a la misma `GameSession` y a la tablet.

Ejemplo:

```text
Nombre: Equipo A
Sesion: Sesion INF-101
Codigo grupo: A
Tablet: Tablet A
```

8. Vuelve al login:

```text
http://127.0.0.1:8000/login/
```

Selecciona `Tableta`, ingresa el PIN generado en `codigo_acceso` y presiona `Iniciar sesion`.

Si el PIN es correcto, la aplicacion redirige a:

```text
/login/home_estudiante/
```

Desde esa pantalla se puede iniciar la ruta visual del juego.

Para que las etapas posteriores tengan contenido real, tambien se recomienda crear en Django Admin al menos:

- Un `Topic` activo.
- Un `Challenge` activo asociado al topic.
- Un `Desafio` activo asociado al challenge.

Sin esos datos, el home puede abrir, pero la seleccion de temas y desafios de las etapas no tendra informacion completa.

## Archivos importantes

- `proyecIngSoft/manage.py`: comando principal de administracion Django.
- `proyecIngSoft/proyecIngSoft/settings.py`: configuracion general del proyecto.
- `proyecIngSoft/requirements.txt`: dependencias Python.
- `proyecIngSoft/docker-compose.yml`: configuracion de ejecucion con Docker.
- `proyecIngSoft/Dockerfile`: imagen Docker de la aplicacion.

## Base de datos

El proyecto esta configurado para usar SQLite:

```text
proyecIngSoft/db.sqlite3
```

Este archivo se considera local y no deberia subirse al repositorio, salvo que el equipo decida compartir una base de datos inicial para fines academicos.

Para crear la base de datos desde cero:

```bash
cd proyecIngSoft
python manage.py migrate
```

## Archivos estaticos y media

El proyecto usa:

- `static/` para archivos estaticos fuente del proyecto.
- `staticfiles/` para archivos generados por `collectstatic`.
- `media/` para archivos subidos durante la ejecucion.

Normalmente se versiona `static/`, pero no `staticfiles/` ni `media/`.

Para recolectar archivos estaticos en produccion:

```bash
python manage.py collectstatic
```

## Buenas practicas de Git

No subir al repositorio:

- Entornos virtuales: `venv/`, `.venv/`, `.venv_local/`
- Variables de entorno: `.env`
- Base de datos local: `db.sqlite3`
- Archivos generados: `__pycache__/`, `*.pyc`, `staticfiles/`
- Archivos subidos por usuarios: `media/`

Si se necesita documentar las variables de entorno, usar un archivo `.env.example` sin secretos reales.

## Notas de seguridad

Actualmente el proyecto esta orientado a desarrollo academico. Antes de desplegar en produccion se recomienda revisar:

- Mover `SECRET_KEY` a variables de entorno.
- Configurar `DEBUG=False`.
- Definir `ALLOWED_HOSTS` con dominios reales.
- Usar una base de datos de produccion si corresponde.
- Proteger correctamente las credenciales de OpenAI.

## Autores

Proyecto desarrollado para el ramo de Ingenieria de Software, ano 2025.
