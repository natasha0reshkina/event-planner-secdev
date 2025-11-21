# syntax=docker/dockerfile:1.7-labs

############################
# 1) build stage
############################
FROM python:3.12-slim AS build

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --no-cache-dir --upgrade "pip==24.3.1" && \
    python -m pip install --no-cache-dir --prefix=/install -r requirements.txt


############################
# 2) runtime stage
############################
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# создаём отдельного пользователя
RUN groupadd -r app && useradd -r -g app app

# копируем только установленные зависимости
COPY --from=build /install /usr/local

# копируем исходники приложения
COPY . .

# даём права пользователю app
RUN chown -R app:app /app

USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "-m", "app.main"]
