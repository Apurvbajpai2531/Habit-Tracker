# Multistage Dockerfile for Habit tracker

# Stage 1 : builder file 

FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

# Install deps into a separate directory — easy to copy to runner
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2 : RUNNER stage 

FROM python:3.12-slim as runner

WORKDIR /app

#RUN addgroup --system app && adduser --system --group app
RUN addgroup --system app \
    && adduser --system --group --home /home/app app \
    && mkdir -p /home/app/.streamlit \
    && chown -R app:app /home/app

  # We add ENV HOME=/home/app because Streamlit needs to know where to write its settings, 
  # and without telling it the right folder, it tries the wrong place and crashes.

ENV HOME=/home/app \
    PYTHONUNBUFFERED=1


COPY --from=builder /install /usr/local
# Copy app code
COPY --chown=app:app . .

USER app

EXPOSE 8501

# Streamlit specific flags for container environments
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.fileWatcherType=none"]
