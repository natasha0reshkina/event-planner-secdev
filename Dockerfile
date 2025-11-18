# syntax=docker/dockerfile:1.7-labs

############################
# 1) build stage
############################
FROM python:3.12-slim AS build

WORKDIR /app

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache \
    python -m pip install --upgrade "pip==24.3.1" && \
    python -m pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt


############################
# 2) runtime stage
############################
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN groupadd -r app && useradd -r -g app app

COPY --from=build /wheels /wheels

RUN python -m pip install --no-cache-dir /wheels/*

COPY . .

RUN chown -R app:app /app

USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "-m", "app.main"]
