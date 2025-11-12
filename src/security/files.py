from pathlib import Path
import uuid

MAX_BYTES = 5_000_000
PNG = b"\x89PNG\r\n\x1a\n"
JPEG_SOI = b"\xff\xd8"
JPEG_EOI = b"\xff\xd9"


def _sniff_image(data: bytes) -> str | None:
    if data.startswith(PNG):
        return "image/png"
    if data.startswith(JPEG_SOI) and data.endswith(JPEG_EOI):
        return "image/jpeg"
    return None


def secure_save(root: Path, data: bytes) -> str:
    if len(data) > MAX_BYTES:
        raise ValueError("too_big")

    mt = _sniff_image(data)
    if mt is None:
        raise ValueError("bad_type")

    root = root.resolve(strict=True)
    ext = ".png" if mt == "image/png" else ".jpg"
    name = f"{uuid.uuid4()}{ext}"
    p = (root / name).resolve()

    if not str(p).startswith(str(root)):
        raise ValueError("path_traversal")
    if any(parent.is_symlink() for parent in p.parents):
        raise ValueError("symlink_parent")

    p.write_bytes(data)
    return str(p)
