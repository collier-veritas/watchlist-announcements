from watch.asx import Announcement, parse_announcements, pdf_filename

SAMPLE = {"data": {"symbol": "SND", "items": [
    {"announcementType": "PROGRESS REPORT", "date": "2026-10-25T22:11:04.000Z",
     "documentKey": "2924-03152828-2A1706009", "headline": "Saunders Water Market Update",
     "isPriceSensitive": True, "url": ""},
]}}


def test_parse_announcements_maps_fields():
    [a] = parse_announcements(SAMPLE)
    assert a == Announcement("SND", "2924-03152828-2A1706009", "Saunders Water Market Update",
                             "PROGRESS REPORT", True, "2026-10-25T22:11:04+00:00")


def test_parse_announcements_handles_no_items():
    assert parse_announcements({"data": {"symbol": "XRG"}}) == []


def test_pdf_filename_is_asx_document_id():
    # Matches what staff already receive, e.g. "03152828.pdf".
    [a] = parse_announcements(SAMPLE)
    assert pdf_filename(a) == "03152828.pdf"
