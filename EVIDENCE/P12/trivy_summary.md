# Trivy summary (P12)

Последний отчёт: `EVIDENCE/P12/trivy_report.json`

## Что нашли
- HIGH: уязвимости в python-зависимостях (Jinja2/urllib3/Starlette)

## Что сделали
- обновили версии в `requirements.txt` для устранения HIGH в `jinja2` и `urllib3`

## Что осталось / план
- HIGH в `starlette` тянется транзитивно через FastAPI; план — обновить FastAPI/Starlette до патч-версии и заново прогнать Trivy
