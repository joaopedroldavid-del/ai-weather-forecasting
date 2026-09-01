# AI Weather Forecasting

A weather forecasting API for Brazilian capital cities. It looks at years of
historical hourly weather readings for a given calendar day, computes the
actual statistics (temperature range, precipitation chance, wind, humidity)
deterministically in Python, and uses an LLM (via LangChain) only to turn
those numbers into a short, human-readable forecast narrative — never to
invent or recompute the numbers themselves.

## How it works

1. **Historical data**: hourly weather station readings from INMET's public
   dataset (BDMEP), filtered down to Brazilian capital cities, stored in a
   Supabase Postgres table (`bdmep_forecast`).
2. **Statistics**: for a requested city + date, every historical occurrence
   of that calendar day (e.g. every July 15th on record) is pulled, collapsed
   into one summary per year, then averaged across years — temperature
   (avg/high/low), precipitation chance and average amount, humidity, and
   wind speed.
3. **Narrative**: those already-computed statistics are handed to an LLM
   (OpenAI, via LangChain) with explicit instructions never to invent or
   contradict a number — its only job is to phrase the numbers as a
   readable forecast, hedging more when fewer years of data are available.
4. **API**: a single `POST /forecast` endpoint ties it together.

> **Status**: only São Paulo currently has historical data loaded into
> Supabase. The other capitals' data ingestion is a planned follow-up.

## Stack

| | |
|---|---|
| Language | Python 3.12 |
| Web framework | FastAPI |
| AI / orchestration | LangChain + OpenAI |
| Validation | Pydantic |
| Database | Supabase (Postgres) |
| Testing | Pytest + pytest-cov |

## Architecture

The codebase follows a strict layered architecture — a request always flows
`Controller → Service → Repository`; no layer skips ahead to the next one
(e.g. a controller never touches the repository directly).

```
app/
├── main.py            FastAPI application entry point
├── config/            Centralized settings (env vars) and the Supabase client factory
├── controllers/        HTTP routes — validate input, delegate to services, map errors to status codes
├── services/            Business rules: historical-stats aggregation, forecast orchestration
├── repositories/        Data access — the only layer that talks to Supabase
├── models/               Internal domain entities (typed, normalized data)
├── dtos/                 API request/response contracts (Pydantic)
├── ai/                    LangChain prompts and chains
└── utils/                 Small shared helpers (e.g. unit conversion)
tests/
├── factories/             Builders for test fixtures
├── mocks/                  Fakes for external services (Supabase client, chat model)
└── ...                     Mirrors the app/ layout
```

| Layer | Owns | Never does |
|---|---|---|
| Controllers | HTTP I/O, input validation via DTOs, error → status code mapping | Business logic, direct data access |
| Services | Business rules, orchestrating repositories + AI | HTTP objects, direct database access |
| Repositories | All Supabase reads/writes | Business rules |
| DTOs | API input/output contracts | Any logic |
| Models | Domain entities | Business rules |
| `ai/` | Prompts, LangChain chains, output validation | Deterministic logic that Python can do more reliably |

## API

### `POST /forecast`

Request:
```json
{
  "location": "São Paulo",
  "date": "09-02-2026"
}
```
`date` is `MM-DD-YYYY`.

Response:
```json
{
  "location": "São Paulo",
  "date": "09-02-2026",
  "forecast": {
    "temperature_max": 28.26,
    "temperature_min": 14.38,
    "temperature_avg": 19.68,
    "wind_speed": 6.35,
    "forecast": "cloudy",
    "precipitation": 3.48,
    "years": [2020, 2021, 2022, 2023, 2024]
  },
  "narrative": "On September 2nd in São Paulo, expect a cloudy day..."
}
```
- `location` is matched case/accent-insensitively against known cities
  (e.g. `"sao paulo"` resolves to `"São Paulo"`).
- `forecast.forecast` is a deterministic condition label (`sunny` /
  `cloudy` / `rain` / `unknown`) derived from precipitation chance — not
  chosen by the LLM.
- `years` lists exactly which historical years backed the statistics.

| Status | Meaning |
|---|---|
| `200` | Forecast generated |
| `400` | `date` isn't valid `MM-DD-YYYY` |
| `404` | Unsupported location, or no historical data for that city/date |
| `422` | Malformed request body (missing/invalid fields) |
| `500` | Unexpected failure (logged server-side; no internals leaked) |

### `GET /health`

Liveness check — always `200 {"status": "ok"}` if the process is up.

### `GET /health/ready`

Readiness check — pings Supabase. `200` with
`{"status": "ok", "dependencies": {"supabase": "up"}}`, or `503` with
`"unavailable"` / `"down"` if the database is unreachable.

## Getting started

### Prerequisites
- Python 3.12
- A Supabase project with a `bdmep_forecast` table (see
  [Data model](#data-model) below)
- An OpenAI API key

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in the values below
```

### Environment variables

| Variable | Required | Description |
|---|---|---|
| `SUPABASE_URL` | yes | Your Supabase project URL (bare, no `/rest/v1` suffix) |
| `SUPABASE_SERVICE_ROLE_KEY` | yes | Supabase **service role** key — this is a trusted backend, so it bypasses RLS |
| `OPENAI_API_KEY` | yes | OpenAI API key used for the forecast narrative |
| `FORECAST_MODEL_NAME` | no (default `gpt-4o-mini`) | OpenAI model used for narrative generation |

### Run

```bash
uvicorn app.main:app --reload
```

```bash
curl --location 'http://127.0.0.1:8000/forecast' \
  --header 'Content-Type: application/json' \
  --data '{"location": "São Paulo", "date": "09-02-2026"}'
```

### Test

```bash
pytest                # run the full suite
pytest --cov=app      # with a coverage report
```
Minimum coverage is 80% (enforced via `pytest-cov`, configured in
`pyproject.toml`). Unit tests never hit real external services — Supabase
and the chat model are faked in `tests/mocks/`, with fixtures built via
`tests/factories/`.

## Deployment (Vercel)

This project deploys to Vercel with zero-config Python/FastAPI support —
Vercel auto-detects the `app` instance at `app/main.py` and runs the whole
API as a single Vercel Function. No code changes were needed for this; the
existing entrypoint already matches what Vercel looks for.

1. Connect the repository to a Vercel project (dashboard Git integration,
   or `vercel link` with the CLI).
2. Set the required environment variables under the project's **Settings →
   Environment Variables** (same names as `.env.example`):
   `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `OPENAI_API_KEY`, and
   optionally `FORECAST_MODEL_NAME`. These are read from the real process
   environment in production — no `.env` file is deployed.
3. Push/deploy. `vercel.json` sets a 30s `maxDuration` on the function
   (covers a Supabase query + an OpenAI call) and excludes `tests/**` from
   the deployed bundle. `.python-version` pins the runtime to `3.12`,
   matching local development.
4. To test locally against the exact runtime Vercel uses, install the
   [Vercel CLI](https://vercel.com/docs/cli) and run `vercel dev` instead of
   `uvicorn`.

> Adjust `maxDuration` in `vercel.json` if your Vercel plan caps function
> duration lower than 30s.

## Data model

`bdmep_forecast` mirrors INMET's raw CSV export column-for-column
(Portuguese headers, comma-decimal numbers, all `text` columns — the
repository layer is responsible for parsing/normalizing this into typed
values). The source data and the one-off compilation script used to build
it live in the (gitignored) `data/` directory and are not part of the
application itself.

## Contributing

- **Branches**: `feat/`, `fix/`, `chore/` + a kebab-case description (e.g.
  `feat/previsao-por-capital`).
- **Commits**: imperative mood, English (e.g. `Add payment retry logic`).
- **PRs**: describe the problem and the proposed solution.

## License

MIT — see [LICENSE](LICENSE).
