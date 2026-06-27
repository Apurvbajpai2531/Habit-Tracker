# Multistage Dockerfile for Habit Tracker Backend

# Stage 1: builder
FROM python:3.12-slim AS builder

WORKDIR /app

# psycopg2-binary needs libpq, gcc for some compiled deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: runner
FROM python:3.12-slim AS runner

# libpq needed at runtime for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system app \
    && adduser --system --group --home /home/app app

ENV HOME=/home/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy app code
COPY --chown=app:app . .

USER app

EXPOSE 5000

# Gunicorn is production-grade — never use flask run in prod
CMD ["gunicorn", "app:app", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]