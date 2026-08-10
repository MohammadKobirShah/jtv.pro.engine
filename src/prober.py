"""
Direct Live Stream & Akamai Cookie Prober
Developer: Kobir Shah
"""

import re
import time
from urllib import request
from .utils import get_bst_now, format_bst

class NoRedirectHandler(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def probe_channel_raw(channel_id, token, user_agent="Denver1769", dev_name="Kobir Shah"):
    if not token:
        return None

    probe_url = f"https://game.denver69.fun/Jtv/{token}/Jtv.mpd?id={channel_id}"
    opener = request.build_opener(NoRedirectHandler)
    req = request.Request(probe_url, headers={"User-Agent": user_agent})

    location = None
    try:
        resp = opener.open(req, timeout=8)
        location = resp.headers.get("Location")
    except request.HTTPError as e:
        location = e.headers.get("Location")
    except Exception:
        return None

    if not location:
        return None

    cookie_str, acl_str = "", "/*"
    st_ts, exp_ts = 0, 0

    if "__hdnea__=" in location:
        m = re.search(r"(__hdnea__=st=(\d+)~exp=(\d+)~acl=([^~&]+)~hmac=[^&]+)", location)
        if m:
            cookie_str = m.group(1)
            st_ts = int(m.group(2))
            exp_ts = int(m.group(3))
            acl_str = m.group(4)
        else:
            m_alt = re.search(r"(__hdnea__=[^&\"\'\|\s]+)", location)
            cookie_str = m_alt.group(1) if m_alt else ""

    now_ts = int(time.time())
    rem_sec = max(0, exp_ts - now_ts) if exp_ts else 0

    return {
        "developer": dev_name,
        "id": str(channel_id),
        "status": "VALID" if rem_sec > 0 else "EXPIRED",
        "cookie": cookie_str,
        "acl": acl_str,
        "is_universal": (acl_str == "/*"),
        "starts": format_bst(st_ts),
        "expires": format_bst(exp_ts),
        "remaining": f"{rem_sec // 3600}h {(rem_sec % 3600) // 60}m {rem_sec % 60}s",
        "remaining_seconds": rem_sec,
        "stream_url": location
    }
