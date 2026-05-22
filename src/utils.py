from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
HISTORY_DIR = DATA_DIR / "history"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
LOGS_DIR = OUTPUTS_DIR / "logs"
REPORTS_DIR = OUTPUTS_DIR / "reports"


def ensure_project_dirs() -> None:
    """Cria as pastas usadas pelo pipeline, caso ainda não existam."""
    for directory in [RAW_DIR, PROCESSED_DIR, HISTORY_DIR, LOGS_DIR, REPORTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def execution_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def configure_logging() -> Path:
    ensure_project_dirs()
    log_file = LOGS_DIR / f"monitoramento_susep_{execution_timestamp()}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )

    return log_file


def latest_history_file() -> Path | None:
    files = sorted(HISTORY_DIR.glob("susep_resseguradoras_*.csv"))
    return files[-1] if files else None
