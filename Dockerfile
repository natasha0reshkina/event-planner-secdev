# syntax=docker/dockerfile:1.7-labs

############################
# 1) build stage
############################
FROM python:3.12-slim@sha256:a30a69a5be8cc1ac1b9c1e4ab72e16d58a4f6b30ad0a601418eab7d5e9cb13fb AS build

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache \
    pip install --upgrade pip && \
    pip wheel --wheel-dir=/wheels -r requirements.txt


############################
# 2) runtime stage
############################
FROM python:3.12-slim@sha256:a30a69a5be8cc1ac1b9c1e4ab72e16d58a4f6b30ad0a601418eab7d5e9cb13fb AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# создаём пользователя
RUN groupadd -r app && useradd -r -g app app

# копируем зависимости
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# копируем приложение
COPY . .

# даём права
RUN chown -R app:app /app
USER app

# healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "-m", "app.main"]
