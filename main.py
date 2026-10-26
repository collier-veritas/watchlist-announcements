"""Check the watchlist once and email new announcements.

    python main.py           # respects the Sydney weekday 7am-8pm window
    python main.py --force   # run now regardless of the window (testing)
"""
import os
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from watch import pipeline

ROOT = Path(__file__).resolve().parent


def main(argv):
    cfg = tomllib.loads((ROOT / "config.toml").read_text())
    for k in ("watchlist", "sent_log", "disclaimer"):
        cfg[k] = ROOT / cfg[k]
    now = datetime.now(timezone.utc)
    if "--force" not in argv and not pipeline.in_window(now, cfg["window_start"], cfg["window_end"]):
        print("Outside the Sydney send window; nothing to do.")
        return 0
    pipeline.run(cfg, os.environ, now)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
