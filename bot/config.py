"""Loads config.yaml / sources.yaml and secrets from the environment (.env locally, GitHub secrets in CI)."""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def load_config(path: Path | None = None) -> dict:
    return yaml.safe_load((path or ROOT / "config.yaml").read_text())


def load_sources(path: Path | None = None) -> dict:
    return yaml.safe_load((path or ROOT / "sources.yaml").read_text())


def secret(name: str, required: bool = True) -> str | None:
    value = (os.environ.get(name) or "").strip().strip('"').strip("'") or None
    if required and not value:
        raise RuntimeError(f"Missing secret {name}. Add it to .env (local) or GitHub Actions secrets.")
    return value
