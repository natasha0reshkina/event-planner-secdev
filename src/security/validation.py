from dataclasses import dataclass
from datetime import date, datetime, timezone


@dataclass(frozen=True)
class EventInput:
    title: str
    date_: date
    place: str
    note: str | None = None


def _today_local() -> date:
    return datetime.now(timezone.utc).astimezone().date()


def validate_event(inp: EventInput) -> None:
    if not (1 <= len(inp.title) <= 200):
        raise ValueError("bad_title_length")
    if not (1 <= len(inp.place) <= 200):
        raise ValueError("bad_place_length")
    if inp.note is not None and len(inp.note) > 2000:
        raise ValueError("bad_note_length")
    if inp.date_ < _today_local():
        raise ValueError("past_date")
