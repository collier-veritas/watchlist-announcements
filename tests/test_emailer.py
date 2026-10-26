import base64

from watch.asx import Announcement
from watch.emailer import build_message

A = Announcement("SND", "2924-03152828-2A1706009", "Saunders Water Market Update",
                 "PROGRESS REPORT", True, "2026-10-25T22:11:04+00:00")


def test_subject_is_ticker_dash_headline():
    msg = build_message(A, b"%PDF", ["a@x.com"], "<p>D</p>")
    assert msg["subject"] == "SND - Saunders Water Market Update"


def test_pdf_attached_under_asx_filename():
    msg = build_message(A, b"%PDF-1.7", ["a@x.com"], "<p>D</p>")
    [att] = msg["attachments"]
    assert att["name"] == "03152828.pdf"
    assert base64.b64decode(att["contentBytes"]) == b"%PDF-1.7"


def test_recipients_go_in_to_list():
    msg = build_message(A, b"%PDF", ["a@x.com", "b@x.com"], "")
    assert [r["emailAddress"]["address"] for r in msg["toRecipients"]] == ["a@x.com", "b@x.com"]


def test_body_shows_release_time_in_sydney_and_disclaimer():
    body = build_message(A, b"%PDF", ["a@x.com"], "<p>DISCLAIMER</p>")["body"]["content"]
    assert "9:11am" in body
    assert "Price sensitive" in body
    assert "<p>DISCLAIMER</p>" in body
