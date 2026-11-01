"""What counts as routine admin (never emailed). Price-sensitive always goes out."""
import re

ADMIN_TYPES = {
    "SECURITY HOLDER DETAILS",   # director's interest, substantial holder notices
    "ISSUED CAPITAL",            # cessation, Appendix 2A/3B/3G, buy-back updates
    "LETTER TO SHAREHOLDERS",    # AGM access letters
    "CHAIRMAN'S ADDRESS",        # AGM speeches (sent when flagged price-sensitive)
}

ADMIN_HEADLINE = re.compile("|".join([
    r"appendix 4g",
    r"corporate governance",
    r"conference call",
    r"webinar",
    r"proxy form",
    r"director'?s'? interest",
    r"cessation of securities",
    r"waiver of listing rule",
    r"appendix (2a|3b|3g|3h|3x|3y|3z)\b",
]), re.IGNORECASE)

# NOTICE OF MEETING is admin only when the headline is the meeting paperwork itself.
# Anything else filed under it (e.g. "ASIC Grants Extensions for FY26 Reporting and AGM") is news.
MEETING_PAPERWORK = re.compile("|".join([
    r"notice of (annual )?(general )?meeting",
    r"notice of agm",
    r"results of (meeting|(\d{4} )?agm|resolutions)",
    r"agm results",
    r"listing rule 3\.13\.1",    # AGM date notice
    r"director nominations",
    r"key dates",
    r"letter to shareholders",
]), re.IGNORECASE)


def is_routine_admin(a):
    if a.price_sensitive:
        return False
    if a.type.upper() == "NOTICE OF MEETING":
        return bool(MEETING_PAPERWORK.search(a.headline) or ADMIN_HEADLINE.search(a.headline))
    return a.type.upper() in ADMIN_TYPES or bool(ADMIN_HEADLINE.search(a.headline))
