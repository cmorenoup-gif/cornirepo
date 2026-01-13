# Imagen base oficial de Python
FROM python:3.10-slim

# Evitar buffering de logs
ENV PYTHONUNBUFFERED=1

# Crear directorio de la app
WORKDIR /app

# Copiar requirements.txt y luego instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la app
COPY main.py .

# Puerto que Cloud Run usará (variable de entorno)
ENV PORT=8080

# Comando para iniciar la app con Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "main:app"]
