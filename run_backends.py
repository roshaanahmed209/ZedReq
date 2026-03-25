"""
Single entry point for the ZedReq API and the backoffice API.

Environment variables
-----------------------
START_BACKENDS   ``both`` | ``main`` | ``backoffice`` (default: ``both``)

  - ``both``: run both servers (local / Docker with two published ports).
  - ``main`` / ``backoffice``: run one server — use this on Render (one web service
    per app). Render sets ``PORT``; that value is used when the corresponding
    ``*_PORT`` is not set.

ZEDREQ_HOST      Bind host for main API (default: 0.0.0.0)
ZEDREQ_PORT      Port for main API when START_BACKENDS=both (default: 5000)

BACKOFFICE_HOST  Bind host for backoffice (default: 0.0.0.0)
BACKOFFICE_PORT  Port for backoffice when START_BACKENDS=both (default: 5001)

PORT             Used when START_BACKENDS is ``main`` or ``backoffice`` if the
                 matching ``*_PORT`` is unset (Render injects this).

UVICORN_RELOAD   Set to 1/true/yes to enable ``--reload`` (single-backend modes only).

Optional: loads ``.env`` from the repo root and ``backoffice/.env`` when python-dotenv
is installed (same as running each app from its directory).
"""
from __future__ import annotations

import os
import signal
import sys
import time
from pathlib import Path
from subprocess import Popen
from typing import List

ROOT = Path(__file__).resolve().parent
MAIN_BACKEND_DIR = ROOT / "backend"
BO_BACKEND_DIR = ROOT / "backoffice" / "backend"


def _load_dotenv_files() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    root_env = ROOT / ".env"
    bo_env = ROOT / "backoffice" / ".env"
    if root_env.is_file():
        load_dotenv(root_env)
    if bo_env.is_file():
        load_dotenv(bo_env, override=True)


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or str(raw).strip() == "":
        return default
    return int(raw)


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def _resolve_port(*, single_mode: bool, specific_port_env: str, default: int) -> int:
    if single_mode:
        if os.environ.get(specific_port_env, "").strip():
            return _env_int(specific_port_env, default)
        return int(os.environ.get("PORT", str(default)))
    return _env_int(specific_port_env, default)


def _wait_any(procs: List[Popen]) -> int:
    while True:
        for p in procs:
            code = p.poll()
            if code is not None:
                return code
        time.sleep(0.25)


def main() -> None:
    _load_dotenv_files()

    mode = os.environ.get("START_BACKENDS", "both").strip().lower()
    if mode not in ("both", "main", "backoffice"):
        print(
            f"Invalid START_BACKENDS={mode!r}; use both, main, or backoffice.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not MAIN_BACKEND_DIR.is_dir():
        print(f"Missing main backend directory: {MAIN_BACKEND_DIR}", file=sys.stderr)
        sys.exit(1)
    if not BO_BACKEND_DIR.is_dir():
        print(f"Missing backoffice backend directory: {BO_BACKEND_DIR}", file=sys.stderr)
        sys.exit(1)

    py = sys.executable
    env = os.environ.copy()
    procs: List[Popen] = []

    single_main = mode == "main"
    single_bo = mode == "backoffice"
    reload_ok = (single_main or single_bo) and _truthy("UVICORN_RELOAD")

    if mode in ("both", "main"):
        host = env.get("ZEDREQ_HOST", "0.0.0.0")
        port = _resolve_port(
            single_mode=single_main,
            specific_port_env="ZEDREQ_PORT",
            default=5000,
        )
        cmd = [
            py,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            host,
            "--port",
            str(port),
        ]
        if reload_ok and single_main:
            cmd.append("--reload")
        print(f"[run_backends] Starting ZedReq main API on http://{host}:{port}")
        procs.append(
            Popen(cmd, cwd=str(MAIN_BACKEND_DIR), env=env)  # noqa: S603
        )

    if mode in ("both", "backoffice"):
        host = env.get("BACKOFFICE_HOST", "0.0.0.0")
        port = _resolve_port(
            single_mode=single_bo,
            specific_port_env="BACKOFFICE_PORT",
            default=5001,
        )
        cmd = [
            py,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            host,
            "--port",
            str(port),
        ]
        if reload_ok and single_bo:
            cmd.append("--reload")
        print(f"[run_backends] Starting backoffice API on http://{host}:{port}")
        procs.append(
            Popen(cmd, cwd=str(BO_BACKEND_DIR), env=env)  # noqa: S603
        )

    def shutdown() -> None:
        for p in procs:
            if p.poll() is None:
                p.terminate()
        deadline = time.monotonic() + 15.0
        for p in procs:
            remaining = max(0.0, deadline - time.monotonic())
            try:
                p.wait(timeout=remaining)
            except TimeoutError:
                p.kill()

    def handle_signal(_signum: int, _frame: object | None) -> None:
        shutdown()
        sys.exit(128 + (_signum if _signum < 128 else 0))

    if sys.platform != "win32":
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

    try:
        exit_code = _wait_any(procs)
        shutdown()
        sys.exit(exit_code if exit_code is not None else 1)
    except KeyboardInterrupt:
        shutdown()
        sys.exit(130)


if __name__ == "__main__":
    main()
