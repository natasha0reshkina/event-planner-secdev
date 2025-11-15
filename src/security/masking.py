import logging


def mask_text(value: str | None, visible: int = 2) -> str:
    if not value:
        return ""
    return value[:visible] + "*" * max(0, len(value) - visible)


def safe_note_len(note: str | None) -> int:
    return len(note) if note else 0


logger = logging.getLogger("eventplanner")


def log_event_action(action: str, title: str, place: str, note: str | None) -> None:
    message = (
        f"action={action} title={mask_text(title)} "
        f"place={mask_text(place)} note_len={safe_note_len(note)}"
    )
    logger.info(message)
