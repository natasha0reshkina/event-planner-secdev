from datetime import date
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import JSONResponse

from src.security.errors import problem
from src.security.files import secure_save
from src.security.masking import safe_note_len
from src.security.validation import EventInput, validate_event

app = FastAPI(title="Event Planner MVP")

_DB: dict[str, dict] = {}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/events")
async def create_event(payload: dict):
    try:
        inp = EventInput(
            title=str(payload.get("title", "")).strip(),
            place=str(payload.get("place", "")).strip(),
            date_=date.fromisoformat(payload["date"]),
            note=payload.get("note"),
        )
        validate_event(inp)
    except (KeyError, ValueError) as e:
        return problem(422, "Неверные данные", str(e))

    new_id = str(len(_DB) + 1)
    _DB[new_id] = {
        "title": inp.title,
        "place": inp.place,
        "date": inp.date_.isoformat(),
        "note_len": safe_note_len(inp.note),
    }
    return {"id": new_id}


@app.put("/events/{event_id}")
async def update_event(event_id: str, payload: dict):
    if event_id not in _DB:
        return problem(404, "Не найдено", "event_not_found")

    try:
        inp = EventInput(
            title=str(payload.get("title", "")).strip(),
            place=str(payload.get("place", "")).strip(),
            date_=date.fromisoformat(payload["date"]),
            note=payload.get("note"),
        )
        validate_event(inp)
    except (KeyError, ValueError) as e:
        return problem(422, "Неверные данные", str(e))

    _DB[event_id].update(
        {
            "title": inp.title,
            "place": inp.place,
            "date": inp.date_.isoformat(),
            "note_len": safe_note_len(inp.note),
        }
    )
    return {"ok": True}


@app.post("/events/{event_id}/image")
async def upload_event_image(event_id: str, file: UploadFile):
    data = await file.read()
    try:
        stored_path = secure_save(Path("storage/images"), data)
    except ValueError as e:
        return problem(422, "Неверный файл", str(e))

    return {"path": stored_path}


@app.exception_handler(Exception)
async def default_handler(request: Request, exc: Exception) -> JSONResponse:
    return problem(500, "Внутренняя ошибка", "internal_error")
