"""Launch the FastAPI agent backend and the Next.js frontend together.

Run this file from the repository root to start:
- Chatbot/main_agent.py on http://127.0.0.1:8000
- Frontend Next.js dev server on http://127.0.0.1:3000
"""

from __future__ import annotations

import signal
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
CHATBOT_DIR = ROOT_DIR / "Chatbot"
FRONTEND_DIR = ROOT_DIR / "Frontend"


def start_process(command: list[str], cwd: Path, label: str) -> subprocess.Popen:
    print(f"Starting {label} in {cwd}...")
    return subprocess.Popen(command, cwd=str(cwd))


def main() -> int:
    backend = start_process(
        [sys.executable, "main_agent.py"],
        cwd=CHATBOT_DIR,
        label="backend agent API",
    )

    frontend = start_process(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        label="frontend dev server",
    )

    def shutdown(*_args):
        for process in (frontend, backend):
            if process.poll() is None:
                process.terminate()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        frontend.wait()
    except KeyboardInterrupt:
        shutdown()
    finally:
        shutdown()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())