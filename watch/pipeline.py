"""One check: fetch watchlist announcements, email new non-admin ones, record them."""
import json
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from watch import asx, emailer
from watch.rules import is_routine_admin

SYDNEY = ZoneInfo("Australia/Sydney")
MAX_AGE = timedelta(hours=18)    # never send older news, even if the sent-log is lost
KEEP_SENT = timedelta(days=30)


def load_watchlist(path):
    tickers = []
    for line in Path(path).read_text().splitlines():
        t = line.split("#")[0].strip().upper()
        if t and t not in tickers:
            tickers.append(t)
    return tickers


def in_window(now, start, end):
    local = now.astimezone(SYDNEY)
    return local.weekday() < 5 and time.fromisoformat(start) <= local.time() < time.fromisoformat(end)


def select_to_send(announcements, sent, now):
    fresh = [a for a in announcements
             if a.key not in sent
             and now - datetime.fromisoformat(a.released) <= MAX_AGE
             and not is_routine_admin(a)]
    return sorted(fresh, key=lambda a: a.released)


def load_sent(path):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else None


def save_sent(path, sent, now):
    cutoff = (now - KEEP_SENT).isoformat()
    kept = {k: v for k, v in sent.items() if v >= cutoff}
    Path(path).write_text(json.dumps(kept, indent=1, sort_keys=True) + "\n")


def run(cfg, env, now, log=print):
    tickers = load_watchlist(cfg["watchlist"])
    found, failed = [], []
    for t in tickers:
        try:
            found += asx.fetch_announcements(t)
        except Exception as e:  # one bad ticker must not block the rest
            failed.append(t)
            log(f"WARN {t}: {e}")
    if len(failed) == len(tickers):
        raise RuntimeError("ASX unreachable for every ticker")

    sent = load_sent(cfg["sent_log"])
    if sent is None:
        # First run: remember what's already out there instead of emailing history.
        save_sent(cfg["sent_log"], {a.key: now.isoformat() for a in found}, now)
        log(f"Seeded sent-log with {len(found)} existing announcements; nothing emailed.")
        return 0

    to_send = select_to_send(found, sent, now)
    for a in found:
        if a.key not in sent and a not in to_send:
            sent[a.key] = now.isoformat()   # skipped admin/stale: don't re-evaluate
    if not to_send:
        save_sent(cfg["sent_log"], sent, now)
        log(f"Checked {len(tickers)} tickers: nothing new.")
        return 0

    recipients = [r.strip() for r in env["RECIPIENTS"].split(",") if r.strip()]
    disclaimer = Path(cfg["disclaimer"]).read_text(encoding="utf-8")
    token = emailer.graph_token(env)
    for a in to_send:
        msg = emailer.build_message(a, asx.fetch_pdf(a), recipients, disclaimer)
        emailer.send(msg, cfg["sender"], token)
        sent[a.key] = now.isoformat()
        save_sent(cfg["sent_log"], sent, now)   # after each send, so a crash can't double-send
        log(f"SENT {msg['subject']}")
    return len(to_send)
