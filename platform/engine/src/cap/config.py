"""Load and expose config.yaml as a simple namespace."""

from __future__ import annotations

import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]


class Config(dict):
    """dict with attribute access; nested dicts wrapped on the fly."""

    def __getattr__(self, key):
        try:
            v = self[key]
        except KeyError as e:
            raise AttributeError(key) from e
        return Config(v) if isinstance(v, dict) else v


def load(path: str | pathlib.Path | None = None, **overrides) -> Config:
    cfg = Config(yaml.safe_load((pathlib.Path(path) if path else ROOT / "config.yaml").read_text()))
    cfg.update(overrides)
    cfg["root"] = str(ROOT)
    return cfg


def data_dir(cfg: Config) -> pathlib.Path:
    p = pathlib.Path(cfg.data_dir)
    if p.is_absolute():
        return p
    # CLI-relative paths resolve from the caller's CWD first, then repo ROOT
    cwd = pathlib.Path.cwd() / p
    return cwd if cwd.exists() else ROOT / p


def out_dir(cfg: Config, stage: str) -> pathlib.Path:
    p = pathlib.Path(cfg.out_dir)
    p = p if p.is_absolute() else ROOT / p
    d = p / stage
    d.mkdir(parents=True, exist_ok=True)
    return d
