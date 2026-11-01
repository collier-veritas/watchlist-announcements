"""What counts as routine admin (never emailed). Price-sensitive always goes out."""
import re

ADMIN_TYPES = {
    "SECURITY HOLDER DETAILS",   # director's interest, substantial holder notices
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


def _any(*patterns):
    return re.compile("|".join(patterns), re.IGNORECASE)


# Types that are admin only when the headline is the routine form itself. Anything else
# filed under them is news, e.g. XRG "ASIC Grants Extensions for FY26 Reporting and AGM"
# (NOTICE OF MEETING) or EOL "GMSL Acquisition Completion" (ISSUED CAPITAL).
ADMIN_FORMS = {
    "NOTICE OF MEETING": _any(
        r"notice of (annual )?(general )?meeting",
        r"notice of agm",
        r"results of (meeting|(\d{4} )?agm|resolutions)",
        r"agm results",
        r"listing rule 3\.13\.1",    # AGM date notice
        r"director nominations",
        r"key dates",
        r"letter to shareholders",
    ),
    "ISSUED CAPITAL": _any(
        r"proposed issue of securities",
        r"application for quotation",
        r"unquoted securities",
        r"buy-?back",
        r"cleansing notice",
        r"section 708a",
    ),
}


def is_routine_admin(a):
    if a.price_sensitive:
        return False
    if ADMIN_HEADLINE.search(a.headline):
        return True
    forms = ADMIN_FORMS.get(a.type.upper())
    if forms:
        return bool(forms.search(a.headline))
    return a.type.upper() in ADMIN_TYPES
