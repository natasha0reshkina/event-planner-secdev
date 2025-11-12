def mask_email(s: str | None) -> str | None:
    if not s:
        return None
    name, _, dom = s.partition("@")
    if not dom:
        return s[:2] + "***"
    return name[:2] + "***@" + dom


def safe_note_len(note: str | None) -> int:
    return len(note or "")
