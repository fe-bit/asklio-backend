FROM python:3.13-slim

# Set work directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy only necessary files for production
COPY pyproject.toml README.md ./
COPY src ./src

# Install only main dependencies (no dev tools)
RUN poetry install --no-root --only main

# Expose port
EXPOSE 8000

# Set environment variables for production (override with your own .env in deployment)
ENV PYTHONUNBUFFERED=1

# Copy .env if present (optional, recommended to use secrets manager or env vars in production)
COPY .env .env

# Use Gunicorn with Uvicorn workers for production
CMD ["poetry", "run", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "src.main:app", "--bind", "0.0.0.0:8000", "--workers", "4"]