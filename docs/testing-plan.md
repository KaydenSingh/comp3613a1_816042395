# Assignment 2 testing plan

## Scope

The test suite covers the existing Alumni App behavior from Assignment 1:

- Event input validation and event search behavior.
- User registration, password verification, and connection-list operations.
- The health endpoint and the existing `/api/users` JSON endpoint.
- Login cookies and access to the authenticated home page.
- Public event search, event details, and the not-found path.

No new application features or API endpoints are introduced for Assignment 2.

## Unit test plan

| Area | Cases |
| --- | --- |
| `EventCreate` | Required values are trimmed; blank title/time/location values are rejected. |
| `AuthService` | Registration hashes the password; valid credentials authenticate; invalid credentials fail. |
| `UserRepository` | Connections are idempotent, removable, and reject self-connections. |
| `EventRepository` | Search matches title and location text. |

Unit tests live in `tests/unit/test_domain.py`.

## Integration test plan

| Endpoint/workflow | Cases |
| --- | --- |
| `GET /health` | Returns the JSON health marker. |
| `GET /api/users` | Serializes users without exposing passwords. |
| `POST /login` and `GET /app` | Successful login sets the access-token cookie and opens the authenticated page. |
| `GET /search` and `GET /search/events/{eventid}` | Search returns matching events; details show the event host. |
| `GET /search/events/{eventid}` | Missing event returns HTTP 404. |

Integration tests use an isolated in-memory SQLite database and live in
`tests/integration/test_http.py`. The production database is never modified.

## Running the tests

From the repository root:

```powershell
python -m pytest -q
```

The tests require the packages in `requirements.txt`. They do not require a
running Uvicorn server, Render, or Postman.

## Postman collection

`postman/AlumniConnect.postman_collection.json` is a runnable collection for a
running local app. Start the app with `python manage.py run`, import the
collection, and run it in order with the `base_url` variable set to
`http://127.0.0.1:5000`.

The collection uses the seeded `admin` account for the protected event-create
request and stores a generated event title for the later search assertion.
Postman tests check status codes, response JSON, redirect cookies, and expected
response content.

## Known limitations and blockers

- The repository exposes only `GET /api/users` as a JSON API. Event search,
  login, and event management are existing HTML form/view routes, so the
  Postman collection tests those routes as HTTP requests rather than inventing
  JSON endpoints.
- A repository-generated student name, student ID, and screenshots cannot be
  produced by these tests. Those remain submission-specific PDF/video inputs.
