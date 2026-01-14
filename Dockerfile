# 1. Imagen base estable (Python 3.10) [cite: 2]
FROM python:3.10-slim

# 2. Configuración de entorno para evitar retrasos en logs
ENV PYTHONUNBUFFERED=1

# 3. Directorio de trabajo en el contenedor
WORKDIR /app

# 4. Instalación de dependencias (Capa de caché optimizada)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copiar el código modular (Muy importante para el nuevo diseño)
# Esto copia main.py y todos los módulos (.py) de la carpeta raíz
COPY *.py ./

# 6. Puerto de escucha de Cloud Run [cite: 4]
ENV PORT=8080

# 7. Ejecución con Gunicorn (Optimizado para producción)
# Se usa 'main:app' asumiendo que tu objeto Flask está en main.py
CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "8", "--timeout", "0", "main:app"]
