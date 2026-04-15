# Usamos Python 3.11 versión ligera
FROM python:3.11-slim

# Variables de entorno para optimizar Python en Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalamos dependencias del sistema (gcc y libpq-dev)
# Esto es necesario porque en tu requirements.txt tienes 'psycopg2' y otras libs
# que a veces requieren compilación, aunque usemos SQLite.
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiamos los requerimientos e instalamos
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código del proyecto
COPY . /app/

# Recolectamos los archivos estáticos (CSS/JS) para que se vea el diseño
# (Requiere que hayas configurado STATIC_ROOT y whitenoise en settings.py)
RUN python manage.py collectstatic --noinput

# Exponemos el puerto 8000
EXPOSE 8000

# Comando para iniciar el servidor de producción
# IMPORTANTE: "proyecIngSoft" es el nombre de la carpeta que contiene wsgi.py
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "proyecIngSoft.wsgi:application"]