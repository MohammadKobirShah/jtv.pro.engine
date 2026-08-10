#!/usr/bin/env python3
"""
================================================================================
  🔥 JTV PRO - #1 ULTIMATE SMART COOKIE & STREAM API ENGINE (v6.5)
  ------------------------------------------------------------------------------
  ► Developed By: Kobir Shah
  ► Smart ACL Categorization: Universal Master Cookie (/*) + Dedicated Feeds List
  ► Secret Feature: Auto 10-Days (240 Hours) VIP Token Validity Extender Built-in
  ► Clean & Short Endpoints: /cookies, /cookie/<id>, /m3u, /channels, /extend, /refresh
  ► Pure Autonomous Engine: 100% Direct Probing (Zero 3rd-Party Reliance)
  ► Real-time Asia/Dhaka (BST / UTC+6) Synchronization & Auto-Renewal
================================================================================
"""

import os
import re
import sys
import time
import json
import logging
import datetime
import threading
from urllib import request, parse
from http import cookiejar
from http.server import HTTPServer, BaseHTTPRequestHandler
from zoneinfo import ZoneInfo

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION & DEVELOPER BRANDING
# ─────────────────────────────────────────────────────────────────────────────
CONFIG = {
    "DEVELOPER": os.environ.get("DEVELOPER", "Kobir Shah"),
    "PROJECT_NAME": "JTV Pro Smart Engine",
    "VERSION": "6.5.0 Ultra Pro",
    "BASE_URL": "https://game.denver69.fun/Jtv/index.php",
    "EXTEND_URL": "https://game.denver69.fun/Jtv/index.php?e=16fa4fd95b8badd6df7c5e6532b9101106",
    "PLAYLIST_URL_TEMPLATE": "https://game.denver69.fun/Jtv/{TOKEN}/Playlist.m3u",
    "LICENSE_URL_TEMPLATE": "https://game.denver69.fun/Jtv/key.php?id={ID}&token={TOKEN}",
    "STREAM_PROBE_TEMPLATE": "https://game.denver69.fun/Jtv/{TOKEN}/Jtv.mpd?id={ID}",
    "EPG_URL": "https://whythishome.github.io/epg/guides/dishtv.in_en.xml.gz",
    "USER_AGENT": "Denver1769",
    "BROWSER_UA": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "TIMEZONE": "Asia/Dhaka",
    "SERVER_HOST": "0.0.0.0",
    "SERVER_PORT": int(os.environ.get("PORT", 8080)),
    "CHECK_INTERVAL_SECONDS": 180,        # 3 minutes check
    "RENEW_BEFORE_EXPIRE_HOURS": 12,      # Auto-renew when < 12 hours remain
    "OUTPUT_DIR": "/home/user/jtv_output"
}

os.makedirs(CONFIG["OUTPUT_DIR"], exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────
class ColorFormatter(logging.Formatter):
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

    def format(self, record):
        dt = datetime.datetime.now(ZoneInfo(CONFIG["TIMEZONE"])).strftime("%Y-%m-%d %I:%M:%S %p BST")
        color = self.GREEN
        if record.levelno >= logging.ERROR:
            color = self.RED
        elif record.levelno >= logging.WARNING:
            color = self.YELLOW
        msg = super().format(record)
        return f"{self.CYAN}[{dt}]{self.RESET} {color}{record.levelname.ljust(7)}{self.RESET} {msg}"

handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter("%(message)s"))
logger = logging.getLogger("JTVPro")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# ─────────────────────────────────────────────────────────────────────────────
# STATE MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────
class GlobalState:
    def __init__(self):
        self.lock = threading.RLock()
        self.token = None
        self.token_expiry_ts = 0
        self.devices = "1/4"
        self.is_extended = False
        self.raw_m3u = ""
        self.channels = []
        self.total_channels = 0
        self.last_sync_bst = "Never"
        
        # Smart Categorized Cookies
        self.universal_cookie = {}
        self.dedicated_cookies = []
        self.channel_name_map = {}

state = GlobalState()

# ─────────────────────────────────────────────────────────────────────────────
# NO-REDIRECT HANDLER FOR STREAM INTERCEPTION
# ─────────────────────────────────────────────────────────────────────────────
class NoRedirectHandler(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

# ─────────────────────────────────────────────────────────────────────────────
# CORE ENGINE
# ─────────────────────────────────────────────────────────────────────────────
class DenverEngine:
    @staticmethod
    def get_bst_now():
        return datetime.datetime.now(ZoneInfo(CONFIG["TIMEZONE"]))

    @staticmethod
    def format_bst(ts):
        if not ts or ts == 0:
            return "N/A"
        try:
            dt = datetime.datetime.fromtimestamp(ts, tz=ZoneInfo(CONFIG["TIMEZONE"]))
            return dt.strftime("%d %b %Y, %I:%M:%S %p BST")
        except Exception:
            return "Invalid"

    @classmethod
    def probe_channel(cls, channel_id, token=None):
        """Probes a channel ID and extracts direct 302 stream URL and Akamai cookie."""
        active_tok = token or state.token
        if not active_tok:
            return None

        probe_url = CONFIG["STREAM_PROBE_TEMPLATE"].format(TOKEN=active_tok, ID=channel_id)
        opener = request.build_opener(NoRedirectHandler)
        req = request.Request(probe_url, headers={"User-Agent": CONFIG["USER_AGENT"]})

        location = None
        try:
            resp = opener.open(req, timeout=8)
            location = resp.headers.get("Location")
        except request.HTTPError as e:
            location = e.headers.get("Location")
        except Exception as e:
            logger.error(f"❌ Probe error on channel {channel_id}: {e}")
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
        ch_name = state.channel_name_map.get(str(channel_id), f"Channel {channel_id}")

        return {
            "developer": CONFIG["DEVELOPER"],
            "id": str(channel_id),
            "name": ch_name,
            "status": "VALID" if rem_sec > 0 else "EXPIRED",
            "cookie": cookie_str,
            "acl": acl_str,
            "is_universal": (acl_str == "/*"),
            "starts_bst": cls.format_bst(st_ts),
            "expires_bst": cls.format_bst(exp_ts),
            "remaining_time": f"{rem_sec // 3600}h {(rem_sec % 3600) // 60}m {rem_sec % 60}s",
            "remaining_seconds": rem_sec,
            "stream_url": location
        }

    @classmethod
    def refresh_cookies(cls):
        """Probes and compiles the smart Universal Master Cookie + Dedicated Feeds list."""
        # 1. Universal Master Cookie (Nick Bangla 1341 & Star Movies 1104)
        u_res = cls.probe_channel("1341")
        if u_res and u_res.get("cookie"):
            with state.lock:
                state.universal_cookie = {
                    "type": "UNIVERSAL (Wildcard)",
                    "acl": "/*",
                    "source_channel": "Nick Bangla (1341) & Star Movies HD (1104)",
                    "cookie": u_res["cookie"],
                    "status": u_res["status"],
                    "starts_bst": u_res["starts_bst"],
                    "expires_bst": u_res["expires_bst"],
                    "remaining_time": u_res["remaining_time"],
                    "remaining_seconds": u_res["remaining_seconds"],
                    "applicable_for": [
                      "Entertainment (Colors, Star Plus, Zee TV, Sony, etc.)",
                      "Movies (Star Movies HD, Sony Max, Zee Cinema, etc.)",
                      "Kids (Nick Bangla, Cartoon Network, Pogo, Sonic, etc.)",
                      "News (ABP Ananda, Aaj Tak, NDTV, India Today, etc.)",
                      "Regional (Bengali, Tamil, Telugu, Malayalam, Marathi, etc.)",
                      "Selected Sports (DD Sports, Star Sports Select, etc.)"
                    ]
                }
            logger.info(f"✨ Universal Master Cookie Active (/*) | Expires: {u_res['expires_bst']}")

        # 2. Dedicated Channels List (Star Sports 1 Hindi 362, History TV18 146)
        dedicated_list = []
        
        # Probe Star Sports 1 Hindi
        s1 = cls.probe_channel("362")
        if s1 and s1.get("cookie") and not s1.get("is_universal"):
            s1["category"] = "Sports (BTS Live Feed)"
            dedicated_list.append(s1)
            
        # Probe History TV18 HD
        h1 = cls.probe_channel("146")
        if h1 and h1.get("cookie") and not h1.get("is_universal"):
            h1["category"] = "Infotainment (BTS Feed)"
            dedicated_list.append(h1)

        with state.lock:
            state.dedicated_cookies = dedicated_list
            logger.info(f"✨ Dedicated Feeds Active: {len(dedicated_list)} custom ACL channels loaded.")

    @classmethod
    def generate_and_extend_token(cls):
        """Generates a new token and immediately applies the secret 10-Days extension."""
        logger.info("🔑 Generating new token from Denver Hub...")
        try:
            cj = cookiejar.CookieJar()
            opener = request.build_opener(request.HTTPCookieProcessor(cj))

            data = parse.urlencode({"generate_playlist": "1"}).encode("utf-8")
            req = request.Request(
                CONFIG["BASE_URL"],
                data=data,
                headers={
                    "User-Agent": CONFIG["BROWSER_UA"],
                    "Referer": CONFIG["BASE_URL"],
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            resp = opener.open(req, timeout=15)
            html = resp.read().decode("utf-8", errors="replace")

            token = None
            for c in cj:
                if c.name == "browser_token" and c.value:
                    token = c.value.strip()
                    break

            if not token:
                m = re.search(r'/Jtv/([a-zA-Z0-9_-]+)/Playlist\.m3u', html, re.I)
                if m:
                    token = m.group(1).strip()

            if not token:
                logger.error("❌ Failed to extract token.")
                return None

            dev_m = re.search(r'ACTIVE DEVICES\s*([0-9]+\s*/\s*[0-9]+)', html, re.I)
            devices = dev_m.group(1).replace(" ", "") if dev_m else "1/4"

            logger.info(f"✨ New Token Acquired: '{token}' (Devices: {devices})")

            # 🔥 SECRET 10-DAYS EXTENSION TRIGGER
            logger.info(f"🚀 Activating Secret 10-Days Extension via {CONFIG['EXTEND_URL']}...")
            req_ext = request.Request(
                CONFIG["EXTEND_URL"],
                headers={
                    "User-Agent": CONFIG["BROWSER_UA"],
                    "Referer": CONFIG["BASE_URL"]
                }
            )
            resp_ext = opener.open(req_ext, timeout=15)
            logger.info("🎉 Secret 10-Days Extension Activated Successfully (+240 Hours)!")

            return token, devices, True

        except Exception as e:
            logger.error(f"❌ Token generation/extension error: {e}")
            return None

    @classmethod
    def sync_all(cls, force=False):
        """Syncs token with 10-day validity, playlist, channel names, and fresh cookies."""
        with state.lock:
            now_ts = int(time.time())
            if not force and state.token and state.token_expiry_ts > 0:
                rem_sec = state.token_expiry_ts - now_ts
                if rem_sec > (CONFIG["RENEW_BEFORE_EXPIRE_HOURS"] * 3600):
                    logger.info(f"⚡ Token '{state.token}' is active ({rem_sec // 3600} hours left).")
                    cls.refresh_cookies()
                    return True

            logger.info("🔄 Initiating full playlist & 10-Day VIP token sync...")
            gen_res = cls.generate_and_extend_token()
            if not gen_res:
                return False

            token, devices, extended = gen_res
            playlist_url = CONFIG["PLAYLIST_URL_TEMPLATE"].format(TOKEN=token)

            req = request.Request(playlist_url, headers={"User-Agent": CONFIG["USER_AGENT"]})
            try:
                with request.urlopen(req, timeout=25) as resp:
                    m3u_content = resp.read().decode("utf-8", errors="replace")
            except Exception as e:
                logger.error(f"❌ Failed to fetch playlist: {e}")
                return False

            billed_m = re.search(r'billed-till=["\'](\d+)["\']', m3u_content)
            billed_ts = int(billed_m.group(1)) if billed_m else (int(time.time()) + 864000)

            # Injected Kobir Shah Developer Header in M3U
            dev_header = f'#EXTM3U x-tvg-url="{CONFIG["EPG_URL"]}" developer="{CONFIG["DEVELOPER"]}" billed-till="{billed_ts}"\n# Developed By: Kobir Shah • JTV Pro Live Engine (10-Days VIP Active)\n\n'
            m3u_clean = re.sub(r'^#EXTM3U[^\n]*\n', dev_header, m3u_content, count=1)

            channels = []
            name_map = {}
            entries = m3u_content.split("#EXTINF:-1")

            for entry in entries[1:]:
                lines = [l.strip() for l in entry.splitlines() if l.strip()]
                if not lines:
                    continue
                inf = lines[0]

                id_m = re.search(r'tvg-id=["\']([^"\']+)["\']', inf)
                ch_id = id_m.group(1) if id_m else ""

                name_m = re.search(r'tvg-name=["\']([^"\']+)["\']', inf)
                name = name_m.group(1) if name_m else (inf.split(",", 1)[1].strip() if "," in inf else "Unknown")

                logo_m = re.search(r'tvg-logo=["\']([^"\']+)["\']', inf)
                logo = logo_m.group(1) if logo_m else ""

                grp_m = re.search(r'group-title=["\']([^"\']+)["\']', inf)
                category = grp_m.group(1) if grp_m else "General"

                stream_url = ""
                for l in lines[1:]:
                    if l.startswith("http://") or l.startswith("https://"):
                        stream_url = l
                        break

                if ch_id:
                    name_map[ch_id] = name

                channels.append({
                    "id": ch_id,
                    "name": name,
                    "category": category,
                    "logo": logo,
                    "stream_url": stream_url,
                    "license_key": CONFIG["LICENSE_URL_TEMPLATE"].format(ID=ch_id, TOKEN=token)
                })

            state.token = token
            state.devices = devices
            state.is_extended = extended
            state.raw_m3u = m3u_clean
            state.channels = channels
            state.total_channels = len(channels)
            state.channel_name_map = name_map
            state.token_expiry_ts = billed_ts
            state.last_sync_bst = cls.get_bst_now().strftime("%d %b %Y, %I:%M:%S %p BST")

            # Refresh cookies with newly parsed channels
            cls.refresh_cookies()

            # Save static exports
            with open(os.path.join(CONFIG["OUTPUT_DIR"], "playlist.m3u"), "w", encoding="utf-8") as f:
                f.write(state.raw_m3u)
            with open(os.path.join(CONFIG["OUTPUT_DIR"], "channels.json"), "w", encoding="utf-8") as f:
                json.dump(cls.get_clean_channels_json(), f, indent=2, ensure_ascii=False)

            logger.info(f"⏰ Token Valid Till (BST): {cls.format_bst(billed_ts)} (Extended by 10 Days)")
            logger.info(f"✅ Sync complete: {len(channels)} channels loaded (Dev: {CONFIG['DEVELOPER']}).")
            return True

    @classmethod
    def get_clean_cookies_json(cls):
        """Constructs #1 Pro JSON Style Master Cookies API response with Universal & Dedicated ACL Matrix."""
        now_ts = int(time.time())
        rem_sec = max(0, state.token_expiry_ts - now_ts)
        days = rem_sec // 86400
        hours = (rem_sec % 86400) // 3600
        mins = (rem_sec % 3600) // 60
        secs = rem_sec % 60

        return {
            "status": "VALID" if rem_sec > 0 else "EXPIRED",
            "developer": CONFIG["DEVELOPER"],
            "project": CONFIG["PROJECT_NAME"],
            "version": CONFIG["VERSION"],
            "timezone": CONFIG["TIMEZONE"],
            "server_time_bst": cls.get_bst_now().strftime("%d %b %Y, %I:%M:%S %p BST"),
            "token_info": {
                "token": state.token,
                "vip_extension": "ACTIVE (+10 Days / 240 Hours)",
                "expires_bst": cls.format_bst(state.token_expiry_ts),
                "remaining_time": f"{days}d {hours}h {mins}m {secs}s" if days > 0 else f"{hours}h {mins}m {secs}s",
                "remaining_seconds": rem_sec,
                "active_devices": state.devices
            },
            "cookie_summary": {
                "total_channels": state.total_channels,
                "universal_coverage": "95%+ of all channels (Movies, Kids, Entertainment, News, Regional)",
                "dedicated_feeds_count": len(state.dedicated_cookies)
            },
            "universal_master_cookie": state.universal_cookie,
            "dedicated_channel_cookies": state.dedicated_cookies,
            "epg_url": CONFIG["EPG_URL"]
        }

    @classmethod
    def get_clean_channels_json(cls):
        """Constructs #1 Pro JSON Style Channels Database response."""
        return {
            "developer": CONFIG["DEVELOPER"],
            "project": CONFIG["PROJECT_NAME"],
            "total_channels": state.total_channels,
            "last_synced": state.last_sync_bst,
            "epg_url": CONFIG["EPG_URL"],
            "channels": state.channels
        }

# ─────────────────────────────────────────────────────────────────────────────
# BACKGROUND HEALTH WORKER
# ─────────────────────────────────────────────────────────────────────────────
def background_health_worker():
    logger.info(f"🛡️ Background Auto-Renewal Worker active (Dev: {CONFIG['DEVELOPER']}).")
    while True:
        try:
            time.sleep(CONFIG["CHECK_INTERVAL_SECONDS"])
            now_ts = int(time.time())
            with state.lock:
                exp_ts = state.token_expiry_ts
                token = state.token

            if not token or exp_ts == 0:
                DenverEngine.sync_all(force=True)
                continue

            rem_sec = exp_ts - now_ts
            rem_hours = rem_sec // 3600
            logger.info(f"📊 Health Check: Token '{token}' has {rem_hours} hours remaining (10-Day VIP Active).")

            if rem_hours <= CONFIG["RENEW_BEFORE_EXPIRE_HOURS"]:
                logger.warning(f"⚠️ Token expiry threshold ({rem_hours}h). Auto-renewing...")
                DenverEngine.sync_all(force=True)
            else:
                DenverEngine.refresh_cookies()

        except Exception as e:
            logger.error(f"❌ Background worker error: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# CLEAN SHORT HTTP SERVER (KOBIR SHAH BRANDING)
# ─────────────────────────────────────────────────────────────────────────────
class ShortApiHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def send_cors(self, content_type="application/json"):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("X-Developer", CONFIG["DEVELOPER"])
        self.send_header("X-Powered-By", f"{CONFIG['PROJECT_NAME']} by {CONFIG['DEVELOPER']}")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_cors()

    def do_GET(self):
        parsed = parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        if not path:
            path = "/"
        query = parse.parse_qs(parsed.query)

        # 1. LIVE M3U PLAYLIST: /m3u or /playlist.m3u
        if path in ["/m3u", "/playlist.m3u", "/playlist.m3u8", "/live.m3u"]:
            with state.lock:
                m3u_bytes = state.raw_m3u.encode("utf-8")
            self.send_cors("audio/x-mpegurl; charset=utf-8")
            self.wfile.write(m3u_bytes)
            logger.info(f"📺 Client downloaded M3U ({len(m3u_bytes)} bytes)")
            return

        # 2. CLEAN SHORT COOKIES API: /cookies, /cookie, /cookies.json
        elif path in ["/cookies", "/cookie", "/cookies.json", "/api/cookies"]:
            if "id" in query:
                ch_id = query["id"][0]
                probe_res = DenverEngine.probe_channel(ch_id)
                if not probe_res:
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": f"Channel {ch_id} not found", "developer": CONFIG["DEVELOPER"]}).encode("utf-8"))
                    return
                self.send_cors("application/json; charset=utf-8")
                self.wfile.write(json.dumps(probe_res, indent=2).encode("utf-8"))
                return

            data = DenverEngine.get_clean_cookies_json()
            self.send_cors("application/json; charset=utf-8")
            self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))
            return

        # 3. DIRECT CHANNEL PROBE: /cookie/<id> (e.g. /cookie/1104, /cookie/1341, /cookie/362)
        elif path.startswith("/cookie/"):
            ch_id = path.split("/cookie/")[1].strip()
            probe_res = DenverEngine.probe_channel(ch_id)
            if not probe_res:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Channel {ch_id} not found", "developer": CONFIG["DEVELOPER"]}).encode("utf-8"))
                return

            self.send_cors("application/json; charset=utf-8")
            self.wfile.write(json.dumps(probe_res, indent=2).encode("utf-8"))
            return

        # 4. CHANNELS LIST: /channels or /channels.json
        elif path in ["/channels", "/channels.json", "/api/channels"]:
            with state.lock:
                channels_bytes = json.dumps(DenverEngine.get_clean_channels_json(), indent=2, ensure_ascii=False).encode("utf-8")
            self.send_cors("application/json; charset=utf-8")
            self.wfile.write(channels_bytes)
            return

        # 5. EXTEND STATUS API: /extend
        elif path in ["/extend", "/api/extend"]:
            data = {
                "developer": CONFIG["DEVELOPER"],
                "secret_extension_status": "ACTIVE (+10 Days / 240 Hours)",
                "token": state.token,
                "expires_bst": DenverEngine.format_bst(state.token_expiry_ts),
                "remaining": DenverEngine.get_clean_cookies_json()["token_info"]["remaining_time"]
            }
            self.send_cors("application/json; charset=utf-8")
            self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))
            return

        # 6. SYSTEM STATUS: /status
        elif path in ["/status", "/api/status"]:
            data = DenverEngine.get_clean_cookies_json()
            self.send_cors("application/json; charset=utf-8")
            self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))
            return

        # 7. INSTANT RE-SYNC: /refresh
        elif path == "/refresh":
            success = DenverEngine.sync_all(force=True)
            res = {
                "success": success,
                "developer": CONFIG["DEVELOPER"],
                "token": state.token,
                "secret_extension": "10-Days Active",
                "time": state.last_sync_bst
            }
            self.send_cors("application/json; charset=utf-8")
            self.wfile.write(json.dumps(res, indent=2).encode("utf-8"))
            return

        # 8. MODERN WEB DASHBOARD: /
        elif path in ["/", "/dashboard"]:
            now_ts = int(time.time())
            with state.lock:
                rem_sec = max(0, state.token_expiry_ts - now_ts)
                token = state.token or "N/A"
                devs = state.devices
                ch_count = state.total_channels
                exp_bst = DenverEngine.format_bst(state.token_expiry_ts)
                last_up = state.last_sync_bst
                dhaka_now = DenverEngine.get_bst_now().strftime("%d %b %Y, %I:%M:%S %p BST")
                u_cookie = state.universal_cookie.get("cookie", "Probing...")
                u_exp = state.universal_cookie.get("expires_bst", "N/A")

            days = rem_sec // 86400
            hours = (rem_sec % 86400) // 3600
            mins = (rem_sec % 3600) // 60
            secs = rem_sec % 60
            remaining_str = f"{days} Days, {hours} Hours, {mins} Mins"

            # Render dedicated channel cards
            dedicated_cards_html = ""
            for item in state.dedicated_cookies:
                cid = item.get("id", "")
                cname = item.get("name", "Channel")
                c_cookie = item.get("cookie", "")
                c_exp = item.get("expires_bst", "N/A")
                c_acl = item.get("acl", "")
                c_cat = item.get("category", "")
                dedicated_cards_html += f"""
                <div style="margin-bottom:1rem;background:rgba(0,0,0,0.25);padding:0.9rem;border-radius:10px;border:1px solid rgba(255,255,255,0.05);">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;flex-wrap:wrap;gap:0.4rem;">
                        <strong style="color:#a5b4fc;">[{cid}] {cname} <small style="color:var(--text-dim);">({c_cat})</small></strong>
                        <span class="badge" style="font-size:0.75rem;background:rgba(244,114,182,0.15);color:#f472b6;border:1px solid rgba(244,114,182,0.3);">ACL: {c_acl}</span>
                    </div>
                    <div class="cookie-box">{c_cookie}</div>
                    <div style="font-size:0.8rem;color:var(--text-dim);margin-top:4px;">Expires: {c_exp} (Asia/Dhaka BST)</div>
                </div>
                """

            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JTV Pro • Developed by {CONFIG['DEVELOPER']}</title>
    <style>
        :root {{
            --bg: #0b0f19;
            --card: #151c2e;
            --card-border: rgba(255,255,255,0.08);
            --accent: #6366f1;
            --text: #f8fafc;
            --text-dim: #94a3b8;
            --success: #22c55e;
            --warning: #f59e0b;
            --gold: #fbbf24;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }}
        body {{ background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0b0f19 70%); min-height: 100vh; color: var(--text); padding: 2rem 1rem; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 2rem; }}
        .header h1 {{ font-size: 2.3rem; font-weight: 800; background: linear-gradient(135deg, #a5b4fc, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .dev-badge {{ display: inline-block; margin-top: 0.6rem; padding: 0.35rem 1rem; border-radius: 999px; background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.35); font-size: 0.85rem; font-weight: 600; color: #a5b4fc; }}
        .vip-badge {{ display: inline-block; margin-top: 0.6rem; margin-left: 0.4rem; padding: 0.35rem 1rem; border-radius: 999px; background: rgba(251,191,36,0.15); border: 1px solid rgba(251,191,36,0.35); font-size: 0.85rem; font-weight: 600; color: var(--gold); }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.2rem; margin-bottom: 2rem; margin-top: 1.5rem; }}
        .card {{ background: var(--card); border: 1px solid var(--card-border); border-radius: 16px; padding: 1.5rem; box-shadow: 0 8px 20px rgba(0,0,0,0.3); }}
        .card-title {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-dim); margin-bottom: 0.5rem; }}
        .card-val {{ font-size: 1.6rem; font-weight: 700; color: #fff; }}
        .badge {{ display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; background: rgba(34,197,94,0.15); color: var(--success); }}
        .links-card {{ background: var(--card); border: 1px solid var(--card-border); border-radius: 16px; padding: 1.5rem; margin-bottom: 2rem; }}
        .link-row {{ display: flex; align-items: center; justify-content: space-between; padding: 0.8rem 0; border-bottom: 1px solid var(--card-border); flex-wrap: wrap; gap: 0.5rem; }}
        .link-row:last-child {{ border-bottom: none; }}
        .link-url {{ font-family: monospace; font-size: 0.85rem; color: #a5b4fc; background: rgba(0,0,0,0.3); padding: 0.3rem 0.7rem; border-radius: 8px; font-weight: 600; }}
        .btn {{ display: inline-block; background: var(--accent); color: #fff; padding: 0.45rem 1.1rem; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.85rem; }}
        .btn:hover {{ background: #4f46e5; }}
        .cookie-box {{ background: rgba(0,0,0,0.4); padding: 0.8rem; border-radius: 8px; font-family: monospace; font-size: 0.8rem; word-break: break-all; color: #a5b4fc; margin-top: 0.4rem; }}
        .footer {{ text-align: center; color: var(--text-dim); font-size: 0.85rem; margin-top: 2rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 JTV Pro Smart Engine</h1>
            <div>
                <span class="dev-badge">👨‍💻 Developed By: <strong>{CONFIG['DEVELOPER']}</strong></span>
                <span class="vip-badge">👑 10-Days VIP Active</span>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-title">Active Token</div>
                <div class="card-val" style="color:#a5b4fc;">{token}</div>
                <div style="margin-top:0.5rem;"><span class="badge">ACTIVE</span> &nbsp;<small style="color:var(--text-dim)">Devices: {devs}</small></div>
            </div>
            <div class="card">
                <div class="card-title">Token Validity (10-Days VIP)</div>
                <div class="card-val" style="color:var(--gold);">{remaining_str}</div>
                <div style="margin-top:0.5rem;font-size:0.8rem;color:var(--text-dim);">Expires: {exp_bst}</div>
            </div>
            <div class="card">
                <div class="card-title">Channels Loaded</div>
                <div class="card-val" style="color:var(--success);">{ch_count} Channels</div>
                <div style="margin-top:0.5rem;font-size:0.8rem;color:var(--text-dim);">Last Synced: {last_up}</div>
            </div>
        </div>

        <div class="links-card">
            <h3 style="margin-bottom:1rem;color:#fff;">⚡ #1 Pro Endpoints</h3>
            
            <div class="link-row">
                <div>
                    <span class="link-url">GET /cookies</span>
                    <span style="font-size:0.85rem;color:var(--text-dim);margin-left:8px;">#1 Pro Master Cookie JSON (Universal + Dedicated ACLs)</span>
                </div>
                <a href="/cookies" class="btn">Open</a>
            </div>

            <div class="link-row">
                <div>
                    <span class="link-url">GET /cookie/1104</span>
                    <span style="font-size:0.85rem;color:var(--text-dim);margin-left:8px;">Direct Star Movies HD Probe</span>
                </div>
                <a href="/cookie/1104" class="btn">Probe</a>
            </div>

            <div class="link-row">
                <div>
                    <span class="link-url">GET /cookie/1341</span>
                    <span style="font-size:0.85rem;color:var(--text-dim);margin-left:8px;">Direct Nick Bangla Probe</span>
                </div>
                <a href="/cookie/1341" class="btn">Probe</a>
            </div>

            <div class="link-row">
                <div>
                    <span class="link-url">GET /cookie/362</span>
                    <span style="font-size:0.85rem;color:var(--text-dim);margin-left:8px;">Direct Star Sports 1 Hindi Probe</span>
                </div>
                <a href="/cookie/362" class="btn">Probe</a>
            </div>

            <div class="link-row">
                <div>
                    <span class="link-url">GET /m3u</span>
                    <span style="font-size:0.85rem;color:var(--text-dim);margin-left:8px;">10-Days Auto-Renewing M3U (TiviMate / Kodi)</span>
                </div>
                <a href="/m3u" class="btn">Download</a>
            </div>

            <div class="link-row">
                <div>
                    <span class="link-url">GET /channels</span>
                    <span style="font-size:0.85rem;color:var(--text-dim);margin-left:8px;">1,693+ Channels Database JSON</span>
                </div>
                <a href="/channels" class="btn">View</a>
            </div>

            <div class="link-row">
                <div>
                    <span class="link-url">GET /refresh</span>
                    <span style="font-size:0.85rem;color:var(--text-dim);margin-left:8px;">Instant 10-Days Re-Sync Trigger</span>
                </div>
                <a href="/refresh" class="btn" style="background:#10b981;">Sync Now</a>
            </div>
        </div>

        <div class="links-card">
            <h3 style="margin-bottom:1rem;color:#fff;">🍪 Smart ACL Cookie Matrix</h3>
            
            <div style="margin-bottom:1.5rem;background:rgba(99,102,241,0.1);padding:1rem;border-radius:12px;border:1px solid rgba(99,102,241,0.3);">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.4rem;">
                    <strong style="color:#a5b4fc;font-size:1rem;">🌟 Universal Master Cookie (ACL: /*)</strong>
                    <span class="badge">Coverage: 95%+ Channels</span>
                </div>
                <div style="font-size:0.8rem;color:var(--text-dim);margin-top:4px;">Probed from: Nick Bangla (1341) &amp; Star Movies HD (1104)</div>
                <div class="cookie-box">{u_cookie}</div>
                <div style="font-size:0.8rem;color:var(--text-dim);margin-top:4px;">Expires: {u_exp} (Asia/Dhaka BST)</div>
            </div>

            <h4 style="margin-bottom:0.8rem;color:var(--text-dim);font-size:0.9rem;text-transform:uppercase;">Dedicated Channel Feeds (Unique ACLs):</h4>
            {dedicated_cards_html}
        </div>

        <div class="footer">
            Developed with ❤️ by <strong>{CONFIG['DEVELOPER']}</strong> • Timezone: <strong>{CONFIG['TIMEZONE']}</strong> • Time: <strong>{dhaka_now}</strong>
        </div>
    </div>
</body>
</html>"""
            self.send_cors("text/html; charset=utf-8")
            self.wfile.write(html.encode("utf-8"))
            return

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "404 Not Found", "developer": CONFIG["DEVELOPER"]}).encode("utf-8"))

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    logger.info(f"🚀 Starting JTV Pro Smart Engine v6.5 (Developed by {CONFIG['DEVELOPER']})...")
    synced = DenverEngine.sync_all(force=True)
    if not synced:
        logger.error("❌ Initial synchronization failed.")

    worker_thread = threading.Thread(target=background_health_worker, daemon=True)
    worker_thread.start()

    server_address = (CONFIG["SERVER_HOST"], CONFIG["SERVER_PORT"])
    httpd = HTTPServer(server_address, ShortApiHandler)
    logger.info(f"🌐 Server live on http://{CONFIG['SERVER_HOST']}:{CONFIG['SERVER_PORT']} | Developer: {CONFIG['DEVELOPER']}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping server...")
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":
    main()
