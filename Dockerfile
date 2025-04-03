# Use Python 3.10 slim as the base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=1.6.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${POETRY_HOME}/bin:$PATH"

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy project files
COPY . .

# Create non-root user
RUN addgroup --system app && adduser --system --group app
RUN chown -R app:app /app
USER app

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
