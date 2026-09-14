"""Vercel entry — 비공개 데모. 토큰 게이트는 sim.api 안(FABSIM_TOKEN)."""
import os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("FABSIM_DEMO", "1")
os.environ.setdefault("FABSIM_STORE_DIR", "/tmp/fabsim_store")   # Vercel은 /tmp만 쓰기 가능(휘발)
from sim.api import app  # noqa: E402
