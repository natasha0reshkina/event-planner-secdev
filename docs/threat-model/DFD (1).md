# DFD — Data Flow Diagram (Event Planner)

Диаграмма ниже отражает границы доверия (client / edge / core / data) и нумерованные потоки F1…F9.

```mermaid
flowchart LR
  %% Trust Boundaries (use plain names for GitHub)
  subgraph Client
    U[User (Browser/Mobile)]
  end

  subgraph Edge
    BFF[API Gateway / BFF]
  end

  subgraph Core
    SVC[Event Service]
    AUTH[OIDC Provider]
    CAL[Calendar Stub (ICS Export)]
    AUD[Audit Log Service]
  end

  subgraph Data
    DB[(PostgreSQL: events, users)]
    RL[(Rate Limiter / Redis)]
  end

  %% Flows
  U -->|F1: HTTPS /login creds| BFF
  BFF -->|F2: OIDC Auth Code + PKCE| AUTH
  BFF -->|F3: mTLS + JWT (Bearer)| SVC
  U -->|F5: HTTPS /events CRUD JSON| BFF
  BFF -->|F6: mTLS /events*| SVC
  SVC <--> |F4: TCP 5432 (param queries)| DB
  SVC -->|F7: HTTPS /export.ics (scoped)| CAL
  SVC -->|F8: TCP (structured logs)| AUD
  BFF <--> |F9: counters| RL
```

## Список потоков

| ID | Откуда → Куда | Канал/Протокол | Данные/PII                         | Комментарий                                      |
|----|----------------|-----------------|------------------------------------|--------------------------------------------------|
| F1 | U → BFF        | HTTPS           | creds                              | `/login`, ввод логина/пароля или редирект на OIDC |
| F2 | BFF → AUTH     | HTTPS (OIDC)    | auth code                          | Authorization Code + PKCE                        |
| F3 | BFF → SVC      | mTLS + JWT      | session/JWT                        | Внутрипериметровое обращение к API               |
| F4 | SVC ↔ DB       | TCP (Postgres)  | PII (title, date, place, note)     | Параметризованные запросы                        |
| F5 | U → BFF        | HTTPS           | Event payload                      | CRUD `/events`, фильтры `?from=&to=`             |
| F6 | BFF → SVC      | mTLS            | Event DTO                          | Создание/обновление/удаление                     |
| F7 | SVC → CAL      | HTTPS           | ICS (минимум полей)                | Экспорт календаря (заглушка)                     |
| F8 | SVC → AUD      | TCP             | audit/event logs                   | Кто/что/когда (owner, id, op)                    |
| F9 | BFF ↔ RL       | TCP (Redis)     | counters                           | Rate limiting / quotas                           |
