from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, PlainTextResponse, Response

from src.security.errors import problem
from src.security.files import secure_save
from src.security.masking import log_event_action, safe_note_len

app = FastAPI(title="SecDev Course App", version="0.1.0")


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400) -> None:
        self.code = code
        self.message = message
        self.status = status


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
    response.headers.setdefault("Cross-Origin-Embedder-Policy", "require-corp")
    response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")

    if request.url.path in {"/", "/health", "/robots.txt", "/sitemap.xml"}:
        response.headers.setdefault("Cache-Control", "no-store")
        response.headers.setdefault("Pragma", "no-cache")

    return response


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    return JSONResponse(
        status_code=exc.status,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "http_error"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "http_error", "message": detail}},
    )


@app.get("/")
def root():
    return {"service": "event-planner", "status": "ok"}


@app.get("/robots.txt", include_in_schema=False)
def robots():
    return PlainTextResponse("User-agent: *\nDisallow:\n", status_code=200)


@app.get("/sitemap.xml", include_in_schema=False)
def sitemap():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>/</loc></url>
  <url><loc>/health</loc></url>
</urlset>
"""
    return Response(content=xml, media_type="application/xml", status_code=200)


@app.get("/health")
def health():
    return {"status": "ok"}


_EVENTS_DB: dict[str, dict] = {}


def _validate_event(payload: dict) -> None:
    title = str(payload.get("title", "")).strip()
    place = str(payload.get("place", "")).strip()
    raw_date = payload.get("date")

    if not (1 <= len(title) <= 200):
        raise ValueError("bad_title_length")
    if not (1 <= len(place) <= 200):
        raise ValueError("bad_place_length")
    note = payload.get("note")
    if note is not None and len(str(note)) > 2000:
        raise ValueError("bad_note_length")

    try:
        d = date.fromisoformat(raw_date)
    except Exception as err:
        raise ValueError("bad_date_format") from err
    if d < date.today():
        raise ValueError("past_date")


@app.post("/events")
def create_event(payload: dict):
    try:
        _validate_event(payload)
    except ValueError as e:
        return problem(422, "Неверные данные", str(e))

    new_id = str(len(_EVENTS_DB) + 1)
    _EVENTS_DB[new_id] = {
        "title": payload["title"],
        "place": payload["place"],
        "date": payload["date"],
        "note_len": safe_note_len(payload.get("note")),
    }
    log_event_action("create", payload["title"], payload["place"], payload.get("note"))
    return {"id": new_id}


@app.post("/events/{event_id}/image")
async def upload_event_image(event_id: str, file: UploadFile):
    if event_id not in _EVENTS_DB:
        return problem(404, "Не найдено", "event_not_found")

    data = await file.read()
    try:
        stored_path = secure_save(Path("storage/images"), data)
    except ValueError as e:
        return problem(422, "Неверный файл", str(e))
    return {"path": stored_path}
