from __future__ import annotations

import logging
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from celery import shared_task
from django.conf import settings

logger = logging.getLogger("toolverse.ops")


def run_database_backup() -> dict:
    """
    Dump PostgreSQL to BACKUP_DIR when BACKUP_ENABLED=true.
    SQLite installs copy the db file. Returns status dict; never raises for disabled.
    """
    if not getattr(settings, "BACKUP_ENABLED", False):
        return {"status": "skipped", "reason": "BACKUP_ENABLED=false"}

    backup_dir = Path(getattr(settings, "BACKUP_DIR", "/tmp/toolverse-backups"))
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    engine = settings.DATABASES["default"]["ENGINE"]
    if "sqlite" in engine:
        db_name = settings.DATABASES["default"].get("NAME")
        if not db_name:
            return {"status": "error", "error": "sqlite NAME missing"}
        dest = backup_dir / f"toolverse-{stamp}.sqlite3"
        shutil.copy2(db_name, dest)
        return {"status": "ok", "path": str(dest), "engine": "sqlite"}

    # PostgreSQL via pg_dump
    pg_dump = shutil.which("pg_dump")
    if not pg_dump:
        return {"status": "error", "error": "pg_dump not found on PATH"}

    db = settings.DATABASES["default"]
    dest = backup_dir / f"toolverse-{stamp}.sql.gz"
    env = os.environ.copy()
    if db.get("PASSWORD"):
        env["PGPASSWORD"] = str(db["PASSWORD"])

    cmd = [
        pg_dump,
        "-h",
        str(db.get("HOST") or "localhost"),
        "-p",
        str(db.get("PORT") or "5432"),
        "-U",
        str(db.get("USER") or "postgres"),
        "-d",
        str(db.get("NAME") or "toolverse"),
        "-Fc",
        "-f",
        str(dest),
    ]
    try:
        subprocess.run(cmd, check=True, env=env, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        logger.exception("pg_dump failed")
        return {"status": "error", "error": exc.stderr or str(exc)}

    return {"status": "ok", "path": str(dest), "engine": "postgresql"}


@shared_task(name="apps.common.tasks.backup_database_daily")
def backup_database_daily() -> dict:
    result = run_database_backup()
    logger.info("backup_database_daily: %s", result.get("status"))
    return result
