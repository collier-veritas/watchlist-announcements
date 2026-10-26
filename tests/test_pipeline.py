from datetime import datetime, timezone

from watch.asx import Announcement
from watch.pipeline import in_window, load_watchlist, select_to_send

NOW = datetime(2026, 10, 26, 0, 30, tzinfo=timezone.utc)  # 11:30am Sydney, Monday


def ann(key, date="2026-10-25T22:11:04+00:00", type_="PROGRESS REPORT"):
    return Announcement("SND", key, "Market Update", type_, False, date)


def test_new_announcement_is_selected():
    assert select_to_send([ann("k1")], sent={}, now=NOW) == [ann("k1")]


def test_already_sent_announcement_is_skipped():
    assert select_to_send([ann("k1")], sent={"k1": "x"}, now=NOW) == []


def test_routine_admin_is_skipped():
    a = ann("k1", type_="SECURITY HOLDER DETAILS")
    assert select_to_send([a], sent={}, now=NOW) == []


def test_stale_announcement_is_skipped():
    # Guards against blasting old news if the sent-log is ever lost.
    assert select_to_send([ann("k1", date="2026-10-24T22:00:00+00:00")], sent={}, now=NOW) == []


def test_selected_oldest_first():
    a = ann("late", date="2026-10-25T23:00:00+00:00")
    b = ann("early", date="2026-10-25T21:00:00+00:00")
    assert [x.key for x in select_to_send([a, b], sent={}, now=NOW)] == ["early", "late"]


def test_window_open_on_weekday_daytime():
    assert in_window(NOW, start="07:00", end="20:00")


def test_window_closed_on_sydney_saturday():
    sat = datetime(2026, 10, 31, 0, 30, tzinfo=timezone.utc)
    assert not in_window(sat, start="07:00", end="20:00")


def test_window_closed_late_evening():
    late = datetime(2026, 10, 26, 10, 0, tzinfo=timezone.utc)  # 9pm Sydney
    assert not in_window(late, start="07:00", end="20:00")


def test_load_watchlist_ignores_comments_blanks_and_dupes(tmp_path):
    p = tmp_path / "w.txt"
    p.write_text("# coverage\nSPA\n\nrdm  # lowercase ok\nSPA\n")
    assert load_watchlist(p) == ["SPA", "RDM"]
