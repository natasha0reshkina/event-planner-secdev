FROM python:3.12-slim AS build

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --no-cache-dir --upgrade "pip==24.3.1" && \
    python -m pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN groupadd -g 10001 -r app && useradd -u 10001 -r -g app app

COPY --from=build /install /usr/local
COPY . .

RUN chown -R app:app /app

USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD ["python","-c","import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3).read()"]

EXPOSE 8000

CMD ["python", "-m", "app.main"]
