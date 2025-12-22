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

RUN groupadd -r app && useradd -r -g app app

COPY --from=build /install /usr/local
COPY . .

RUN chown -R app:app /app
USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).read()"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
