# Imagen base con Python
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar dependencias
COPY requirements.txt .
COPY run.py .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY app/ ./app

# Exponer puerto
EXPOSE 5000

CMD ["python", "run.py"]
