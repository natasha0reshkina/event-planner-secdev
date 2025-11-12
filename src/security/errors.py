from uuid import uuid4
from starlette.responses import JSONResponse

def problem(status: int, title: str, detail: str, type_: str = "about:blank"):
    cid = str(uuid4())
    payload = {"type": type_, "title": title, "status": status, "detail": detail, "correlation_id": cid}
    return JSONResponse(payload, status_code=status)
