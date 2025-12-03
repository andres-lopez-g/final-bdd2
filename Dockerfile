# Usar imagen base de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer puerto para la aplicación (si fuera web)
# EXPOSE 8000

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1

# Comando por defecto (ejecutar la aplicación)
CMD ["python", "app_moderna.py"]
