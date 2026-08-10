"""
Utility functions & Timezone handlers for JTV Pro Engine
Developer: Kobir Shah
"""

import datetime
from zoneinfo import ZoneInfo

TIMEZONE = "Asia/Dhaka"

def get_bst_now():
    return datetime.datetime.now(ZoneInfo(TIMEZONE))

def format_bst(ts):
    if not ts or ts == 0:
        return "N/A"
    try:
        dt = datetime.datetime.fromtimestamp(ts, tz=ZoneInfo(TIMEZONE))
        return dt.strftime("%d %b %Y, %I:%M:%S %p BST")
    except Exception:
        return "Invalid"
