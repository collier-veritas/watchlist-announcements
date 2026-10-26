from watch.asx import Announcement
from watch.rules import is_routine_admin


def ann(type_, headline, sensitive=False):
    return Announcement("XYZ", "2924-03152828-2A1706009", headline, type_,
                        sensitive, "2026-10-26T00:00:00+00:00")


def test_price_sensitive_is_never_admin():
    assert not is_routine_admin(ann("ISSUED CAPITAL", "Strategic $20M Placement", True))


def test_director_interest_notice_is_admin():
    assert is_routine_admin(ann("SECURITY HOLDER DETAILS", "Change of Director's Interest Notice"))


def test_notice_of_meeting_is_admin():
    assert is_routine_admin(ann("NOTICE OF MEETING", "Notice of Annual General Meeting/Proxy Form"))


def test_cessation_of_securities_is_admin():
    assert is_routine_admin(ann("ISSUED CAPITAL", "Notification of cessation of securities - VRS"))


def test_corporate_governance_statement_is_admin():
    assert is_routine_admin(ann("PERIODIC REPORTS", "Appendix 4G and Corporate Governance Statement"))


def test_conference_call_details_are_admin():
    assert is_routine_admin(ann("PERIODIC REPORTS", "September 2026 Quarterly Results conference call details"))


def test_webinar_notice_is_admin():
    assert is_routine_admin(ann("OTHER", "DEM September Quarter 2026 Results Webinar"))


def test_listing_rule_waiver_is_admin():
    assert is_routine_admin(ann("COMPANY ADMINISTRATION", "ASX Grants Motio a Waiver of Listing Rule 6.23.2"))


def test_non_sensitive_chair_address_is_admin():
    assert is_routine_admin(ann("CHAIRMAN'S ADDRESS", "Chair's Address to Shareholders - AGM"))


def test_non_sensitive_progress_report_is_sent():
    assert not is_routine_admin(ann("PROGRESS REPORT", "Array Technologies Teams with Aeeris"))


def test_chair_resignation_is_sent():
    assert not is_routine_admin(ann("COMPANY ADMINISTRATION", "Future Intention of Chair's Resignation"))


def test_investor_presentation_is_sent():
    assert not is_routine_admin(ann("PERIODIC REPORTS", "September 2026 Quarterly Report presentation"))


def test_dividend_announcement_is_sent():
    assert not is_routine_admin(ann("DISTRIBUTION ANNOUNCEMENT", "Dividend Clarification"))
