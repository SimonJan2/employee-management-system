FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app/

ENV FLASK_APP=app
ENV FLASK_ENV=development

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:create_app()"]