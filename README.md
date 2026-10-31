# Pool.Energy — Tools

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/badge/License-GPL--3.0-blue)](LICENSE)

Small operational utilities for **Pool.Energy**. Each tool lives in its own
directory with its own dependencies and Dockerfile, and is meant to be run
standalone against the public Pool.Energy endpoints.

Today the repository ships one tool: **`pool-logs`**, a WebSocket client that
streams the pool's live partial and payment logs to stdout.

```console
$ python app.py
{'levelname': 'INFO', 'name': 'partials', 'funcName': 'check_and_confirm_partial', 'lineno': 1757, 'timestamp': '2026-10-31T10:48:51.009451+00:00', 'message': 'Farmer fa06effc…e023 updated points from 170 to 171 (+1)'}
{'levelname': 'INFO', 'name': 'partials', 'funcName': 'check_and_confirm_partial', 'lineno': 1757, 'timestamp': '2026-10-31T10:49:08.010355+00:00', 'message': 'Farmer 7322e863…4f5a updated points from 188960 to 189081 (+121)'}
{'levelname': 'INFO', 'name': 'pool', 'funcName': 'create_payment_loop', 'lineno': 1197, 'timestamp': '2026-10-31T10:49:12.934921+00:00', 'message': 'No funds to distribute in pool wallet (fingerprint: 2866622520)'}
{'levelname': 'INFO', 'name': 'partials', 'funcName': 'post_partial', 'lineno': 294, 'timestamp': '2026-10-31T10:49:16.991174+00:00', 'message': 'post_partial response: {new_difficulty: 1}, size: k32, time: 0.0049512386322021484, launcher_id: 0xfa06effc…e023'}
{'levelname': 'INFO', 'name': 'pool', 'funcName': 'submit_payment_loop', 'lineno': 1420, 'timestamp': '2026-10-31T10:49:28.467858+00:00', 'message': 'No payments above minimum, skipping and retrying in 60 seconds'}
```

> Real capture: output produced by `pool-logs` against `wss://pool.energy/ws/log/`.
> Launcher ids are truncated here for readability.

---

## Table of contents

- [Tools](#tools)
- [pool-logs](#pool-logs)
  - [Requirements](#requirements)
  - [Run locally](#run-locally)
  - [Run with Docker](#run-with-docker)
  - [How it works](#how-it-works)
- [Project structure](#project-structure)
- [Adding a tool](#adding-a-tool)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Tools

| Tool        | Description                                                        | Runtime         |
| ----------- | ------------------------------------------------------------------ | --------------- |
| `pool-logs` | Streams live pool logs (partials and payments) from the public API | Python / Docker |

## pool-logs

A single-file asyncio client that subscribes to the pool log WebSocket and
prints every log record as a Python dict, one per line. It is handy to watch
partial validation, farmer difficulty updates and payment activity without
access to the production logs.

### Requirements

- **Python 3.11+**
- Network access to `wss://pool.energy/ws/log/`

### Run locally

```bash
cd pool-logs/src
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python app.py
```

Press `Ctrl+C` to stop; reconnect to resume. The stream has no history beyond
recent lines, so anything printed before the connection is lost.

### Run with Docker

```bash
cd pool-logs
docker build -t pool-energy-pool-logs .
docker run --rm pool-energy-pool-logs
```

The image is based on `python:3.15-alpine`, installs `src/requirements.txt` and
runs `app.py` as the entry point:

```dockerfile
FROM python:3.15-alpine
WORKDIR /app
COPY src/requirements.txt .
COPY src/app.py .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app.py"]
```

### How it works

1. `websockets.connect("wss://pool.energy/ws/log/")` opens the socket.
2. The client sends `["partials", "payments"]` to subscribe to both log
   categories. The server keeps that subscription per connection; sending a
   different list later adds or removes categories.
3. Every received frame is `{"data": [<log record>, …]}`. The client iterates
   over `data`, strips single and double quotes from each `message` field, and
   prints the resulting dict.
4. The loop never exits on its own: a server-side close raises and terminates
   the process.

Log records look like:

```json
{
  "levelname": "INFO",
  "name": "partials",
  "funcName": "post_partial",
  "lineno": 294,
  "timestamp": "2026-10-31T10:49:16.991174+00:00",
  "message": "post_partial response: {new_difficulty: 1}, size: k32, time: 0.0049, launcher_id: 0xfa06effc…"
}
```

The `name` field is the emitting logger (`pool`, `partials`, …) and `levelname`
follows the standard Python logging levels.

## Project structure

```
tools/
├── pool-logs/
│   ├── .dockerignore
│   ├── Dockerfile            # python:3.15-alpine
│   └── src/
│       ├── app.py            # WebSocket client
│       └── requirements.txt  # asyncio 4.0.0, websockets 17.3
├── LICENSE                   # GPL-3.0
└── README.md
```

## Adding a tool

Each tool is self-contained, following the `pool-logs` layout:

1. Create `<tool>/src/` with the script and a `requirements.txt`.
2. Add a `<tool>/Dockerfile` that copies `src/` and sets a `CMD`.
3. Add a `.dockerignore` excluding `__pycache__`, `*.pyc`, `.env`.
4. Document it in the [Tools](#tools) table and give it a section in this
   README (purpose, requirements, usage, how it works).

Tools have no shared package or build system on purpose: nothing to install
together, nothing to break when one tool changes.

## Troubleshooting

| Symptom                                       | Fix                                                             |
| --------------------------------------------- | --------------------------------------------------------------- |
| `ConnectionClosedError` / handshake failures  | Public API unreachable, or the host blocks outbound WebSocket   |
| No output after connecting                    | The pool is quiet; partials and payments are event-driven      |
| `ModuleNotFoundError: websockets`             | Dependencies not installed: `pip install -r requirements.txt`   |
| Docker exits immediately                      | Same as above inside the image; check the build log for pip     |
| Unicode/quote artefacts in `message`          | Expected: the script strips `"` and `'` before printing         |

## License

Distributed under the **GNU General Public License v3.0** — see
[LICENSE](LICENSE).
