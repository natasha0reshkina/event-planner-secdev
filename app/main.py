from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from src.security.errors import problem
from src.security.files import secure_save

app = FastAPI(title="SecDev Course App", version="0.1.0")


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status


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


@app.get("/health")
def health():
    return {"status": "ok"}


_EVENTS_DB: dict[str, dict] = {}


def _validate_event(payload: dict) -> None:
    title = str(payload.get("title", "")).strip()
    place = str(payload.get("place", "")).strip()
    raw_date = payload.get("date")
    if not title:
        raise ValueError("bad_title_length")
    if not place:
        raise ValueError("bad_place_length")
    try:
        d = date.fromisoformat(raw_date)
    except Exception:
        raise ValueError("bad_date_format")
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
        "note_len": len(str(payload.get("note") or "")),
    }
    return {"id": new_id}


@app.post("/events/{event_id}/image")
async def upload_event_image(event_id: str, file: UploadFile):
    data = await file.read()
    try:
        stored_path = secure_save(Path("storage/images"), data)
    except ValueError as e:
        return problem(422, "Неверный файл", str(e))
    return {"path": stored_path}
