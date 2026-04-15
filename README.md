# Mision Emprende

Proyecto web desarrollado con Django para apoyar una experiencia educativa de emprendimiento. La plataforma permite gestionar usuarios, secciones, sesiones, tablets, desafios, etapas de juego, coevaluacion y resultados finales.

## Descripcion

Mision Emprende es una aplicacion orientada a actividades pedagogicas donde estudiantes participan en distintas etapas de un juego formativo. El sistema incluye flujos para estudiantes, profesores y administradores, ademas de integracion con OpenAI para apoyar la evaluacion de pitchs.

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

Desde la carpeta `proyecIngSoft/`, ejecuta:

```bash
docker compose up --build
```

La aplicacion quedara disponible en:

```text
http://127.0.0.1:8000/
```

El archivo `docker-compose.yml` monta la carpeta local dentro del contenedor, por lo que los cambios del codigo se reflejan en el ambiente Docker.

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
