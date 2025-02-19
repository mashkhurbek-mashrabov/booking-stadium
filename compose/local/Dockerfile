# Stage 1: Build dependencies
FROM python:3.11.10-alpine3.20 AS builder

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

# Install build dependencies
RUN apk add --no-cache \
    postgresql-client \
    build-base \
    postgresql-dev \
    linux-headers

# Create and activate virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Python dependencies
COPY ./requirements /requirements
RUN pip install --upgrade pip && \
    pip install -r requirements/development.txt --use-pep517

# Stage 2: Final image
FROM python:3.11.10-alpine3.20

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/scripts:/venv/bin:$PATH"

# Install runtime dependencies only
RUN apk add --no-cache postgresql-client

# Create non-root user
RUN adduser --disabled-password --gecos '' djuser

# Copy virtual environment from builder
COPY --from=builder /venv /venv

# Copy application code and scripts
COPY --chown=djuser:djuser ./app /app
COPY --chown=djuser:djuser ./scripts /scripts


# Create necessary directories and set permissions
RUN mkdir -p /app/vol/static /app/vol/media /app/hr_cache && \
    chown -R djuser:djuser /app && \
    chmod -R 755 /app && \
    chown -R djuser:djuser /app/vol && \
    chmod -R 755 /app/vol && \
    chmod -R +x /scripts

WORKDIR /app
EXPOSE 8031

USER djuser

CMD ["run_local.sh"]