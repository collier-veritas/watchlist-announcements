"""What counts as routine admin (never emailed). Price-sensitive always goes out."""
import re

ADMIN_TYPES = {
    "SECURITY HOLDER DETAILS",   # director's interest, substantial holder notices
    "NOTICE OF MEETING",         # AGM notices, proxy forms, meeting results
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


def is_routine_admin(a):
    if a.price_sensitive:
        return False
    return a.type.upper() in ADMIN_TYPES or bool(ADMIN_HEADLINE.search(a.headline))
