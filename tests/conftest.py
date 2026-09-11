"""Test session defaults (L6, 2026-09-11).

The repository default config.yaml is the v2 research convention (verified-series
price factors, explicit energy retention), which data/sample does not carry.
Tests that exercise the pipeline on data/sample encode the historical (legacy)
behaviour, so the session pins config_legacy.yaml unless CAP_CONFIG is already set.
Tests of the v2 fixes build their own configs and are unaffected.
"""
import os
os.environ.setdefault("CAP_CONFIG", "config_legacy.yaml")
