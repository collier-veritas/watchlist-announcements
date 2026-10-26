import json
from datetime import datetime, timezone

import pytest

from watch import pipeline
from watch.asx import Announcement

NOW = datetime(2026, 10, 26, 0, 30, tzinfo=timezone.utc)
NEWS = Announcement("SND", "2924-03152828-2A1706009", "Market Update", "PROGRESS REPORT",
                    True, "2026-10-25T22:11:04+00:00")
ADMIN = Announcement("SND", "2924-03150000-2A1700000", "Change of Director's Interest Notice",
                     "SECURITY HOLDER DETAILS", False, "2026-10-25T22:00:00+00:00")


@pytest.fixture
def world(tmp_path, monkeypatch):
    (tmp_path / "watchlist.txt").write_text("SND\n")
    (tmp_path / "disclaimer.html").write_text("<p>D</p>")
    w = {"found": [NEWS, ADMIN], "outbox": [],
         "cfg": {"watchlist": tmp_path / "watchlist.txt", "sent_log": tmp_path / "sent.json",
                 "disclaimer": tmp_path / "disclaimer.html", "sender": "ai@x.com"},
         "env": {"RECIPIENTS": "me@x.com"}}
    monkeypatch.setattr(pipeline.asx, "fetch_announcements", lambda t: list(w["found"]))
    monkeypatch.setattr(pipeline.asx, "fetch_pdf", lambda a: b"%PDF")
    monkeypatch.setattr(pipeline.emailer, "graph_token", lambda env: "tok")
    monkeypatch.setattr(pipeline.emailer, "send", lambda msg, sender, token: w["outbox"].append(msg))
    return w


def run(w):
    return pipeline.run(w["cfg"], w["env"], NOW, log=lambda m: None)


def test_first_run_seeds_without_emailing(world):
    assert run(world) == 0
    assert world["outbox"] == []
    assert NEWS.key in json.loads(world["cfg"]["sent_log"].read_text())


def test_new_news_emailed_once_and_admin_never(world):
    world["cfg"]["sent_log"].write_text("{}")
    assert run(world) == 1
    assert run(world) == 0
    assert [m["subject"] for m in world["outbox"]] == ["SND - Market Update"]


def test_send_failure_leaves_announcement_for_retry(world, monkeypatch):
    world["cfg"]["sent_log"].write_text("{}")

    def boom(msg, sender, token):
        raise RuntimeError("graph down")
    monkeypatch.setattr(pipeline.emailer, "send", boom)
    with pytest.raises(RuntimeError):
        run(world)
    assert NEWS.key not in json.loads(world["cfg"]["sent_log"].read_text() or "{}")
