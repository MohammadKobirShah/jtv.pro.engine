# 🔥 JTV Pro Smart Engine

<p align="center">
  <img src="https://img.shields.io/badge/Developer-Kobir%20Shah-blue?style=for-the-badge&logo=github" alt="Developer Kobir Shah"/>
  <img src="https://img.shields.io/badge/Version-6.0.0%20VIP-orange?style=for-the-badge" alt="Version"/>
  <img src="https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-green?style=for-the-badge&logo=python" alt="Python Version"/>
  <img src="https://img.shields.io/badge/Channels-1%2C694%2B%20Live-red?style=for-the-badge&logo=livechat" alt="Channels"/>
  <img src="https://img.shields.io/badge/Timezone-Asia%2FDhaka%20(BST%20%2B06)-purple?style=for-the-badge" alt="Timezone"/>
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" alt="License"/>
</p>

An ultra-fast, autonomous, self-healing **Live TV Stream, ClearKey DRM & Smart Cookie Engine** for 1,694+ Indian & International Channels. Built from scratch with **Zero 3rd-Party Dependencies** (Pure Python 3 Standard Library), featuring automatic token generation, an embedded **+10 Days (240 Hours) VIP secret extender**, and real-time live channel probing (Nick Bangla, Star Movies HD, Star Sports, etc.).

---

## 🌟 Key Highlights

- 👨‍💻 **Developed by:** **Kobir Shah**
- 🚀 **100% Autonomous:** Zero dependency on broken/unmaintained 3rd-party cookie APIs. Directly probes live feeds.
- 👑 **Secret 10-Days VIP Extender:** Automatically extends token validity to **+10 Days (240 Hours)** upon generation.
- 🛡️ **Self-Healing Background Daemon:** Automatically monitors token health every 3 minutes and renews it before expiration.
- 🍪 **Smart Multi-Tier Cookie Engine:**
  - **Universal Master Cookie (`acl=/*`):** Probed from Nick Bangla (`1341`) / Star Movies HD (`1104`) for 95%+ of channels.
  - **Dedicated Sports Cookie:** Probed from Star Sports 1 Hindi (`362`) with dedicated path ACL.
- ⚡ **Clean & Short REST APIs:** Intuitive endpoints like `/cookies`, `/cookie/1104`, `/m3u`, `/channels`, `/extend`, `/refresh`.
- 🇧🇩 **Native Asia/Dhaka (BST / UTC+6) Support:** Real-time human-readable countdowns and timestamps.
- 📺 **IPTV Client Ready:** 100% compatible with TiviMate, OTT Navigator, Kodi, Sparkle TV, VLC, Televizo, and web players.
- 🐳 **Docker & Cloud Ready:** Easy deployment on VPS, Docker, Render, Railway, Koyeb, Termux, or Localhost.

---

## ⚡ Quick Start

### Option 1: Direct Python (No pip install needed!)
```bash
# Clone the repository
git clone https://github.com/kobirshah/jtv-pro-engine.git
cd jtv-pro-engine

# Run the engine
python3 app.py
```

### Option 2: Docker & Docker Compose
```bash
docker-compose up -d
```

The server will be live immediately on `http://localhost:8080` (or `http://YOUR_SERVER_IP:8080`).

---

## 📡 Clean & Short API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | **`/cookies`** | 🍪 **Master Cookies API** (10-Days VIP Status, Universal & Sports Feeds) |
| `GET` | **`/cookie/1104`** | 🎬 **Star Movies HD** instant live cookie probe & stream URL |
| `GET` | **`/cookie/1341`** | 📺 **Nick Bangla** instant live cookie probe & stream URL |
| `GET` | **`/cookie/362`** | 🏏 **Star Sports 1 Hindi** dedicated live cookie & stream URL |
| `GET` | **`/cookie/<id>`** | 🎯 **Any Channel ID** on-demand live cookie & direct stream extractor |
| `GET` | **`/m3u`** | 📺 **Live 10-Days Auto-Renewing M3U Playlist** (For TiviMate, Kodi, OTT Navigator) |
| `GET` | **`/channels`** | 📂 **1,694+ Channels Database JSON** with ClearKey DRM license endpoints |
| `GET` | **`/extend`** | 👑 **VIP 10-Days Extension Status & Expiry Details** |
| `GET` | **`/refresh`** | ⚡ **Instant Token & Cookie Force Re-Sync Trigger** |
| `GET` | **`/`** | 🎛️ **Modern Responsive Web Dashboard & Real-Time Monitor** |

---

## 📋 API Responses Preview

### 1. Master Cookies API (`GET /cookies`)
```json
{
  "status": "VALID",
  "developer": "Kobir Shah",
  "project": "JTV Pro Smart Engine",
  "version": "6.0.0 VIP Edition",
  "secret_extension": "ACTIVE (+10 Days VIP)",
  "timezone": "Asia/Dhaka",
  "server_time": "11 Aug 2026, 01:28:29 AM BST",
  "token": "Ei4Uus",
  "token_expires": "21 Aug 2026, 01:32:35 AM BST",
  "token_remaining": "10d 0h 4m 6s",
  "token_remaining_seconds": 864246,
  "active_devices": "1/4",
  "universal_cookie": {
    "source": "Nick Bangla (1341)",
    "cookie": "__hdnea__=st=1786384839~exp=1786406439~acl=/*~hmac=aa1b63906de851a008589dd69fe4b2fdf53c8307e186adf67e651402849b901e",
    "acl": "/*",
    "expires": "11 Aug 2026, 06:00:39 AM BST",
    "remaining": "4h 32m 14s",
    "status": "VALID"
  },
  "sports_cookie": {
    "source": "Star Sports 1 Hindi (362)",
    "cookie": "__hdnea__=st=1786371020~exp=1786392620~acl=/bpk-tv/Star_Sports_1_Hindi_BTS/WDVLive/*~hmac=fefc7077dbe8d9e4b8724e17b7527b4bf27f923d2adb8d51f7bb30c6c18eb5e0",
    "acl": "/bpk-tv/Star_Sports_1_Hindi_BTS/WDVLive/*",
    "expires": "11 Aug 2026, 02:10:20 AM BST",
    "remaining": "0h 41m 54s",
    "status": "VALID"
  },
  "total_channels": 1693,
  "epg_url": "https://whythishome.github.io/epg/guides/dishtv.in_en.xml.gz"
}
```

### 2. Direct Channel Probe (`GET /cookie/1104` Star Movies HD)
```json
{
  "developer": "Kobir Shah",
  "id": "1104",
  "name": "Star Movies HD",
  "status": "VALID",
  "cookie": "__hdnea__=st=1786384839~exp=1786406439~acl=/*~hmac=aa1b63906de851a008589dd69fe4b2fdf53c8307e186adf67e651402849b901e",
  "acl": "/*",
  "is_universal": true,
  "starts": "11 Aug 2026, 12:00:39 AM BST",
  "expires": "11 Aug 2026, 06:00:39 AM BST",
  "remaining": "4h 32m 9s",
  "remaining_seconds": 16329,
  "stream_url": "https://jiotvmblive.cdn.jio.com/bpk-tv/StarMoviesHD_MOB/WDVLive/index.mpd?__hdnea__=..."
}
```

---

## 📺 How to Use with IPTV Players

1. Open your favorite IPTV app (**TiviMate**, **OTT Navigator**, **Kodi**, or **Sparkle TV**).
2. Add a new **M3U Playlist URL**:
   ```
   http://YOUR_SERVER_IP:8080/m3u
   ```
3. Add the **EPG URL** (Included automatically in M3U header):
   ```
   https://whythishome.github.io/epg/guides/dishtv.in_en.xml.gz
   ```
4. **Done!** You never have to manually update or re-enter tokens again. The server handles token generation, 10-days VIP extension, and DRM key renewals automatically in the background.

---

## 🛠️ Project Structure

```
jtv-pro-engine/
├── .github/
│   └── workflows/
│       └── docker-build.yml       # Automated CI/CD Docker workflow
├── config/
│   └── config.example.json        # Example configuration
├── src/
│   ├── __init__.py
│   ├── engine.py                  # Core token generator, secret extender & sync logic
│   ├── prober.py                  # Live stream & Akamai cookie prober
│   ├── server.py                  # HTTP REST API & Web Dashboard handler
│   └── utils.py                   # Timezone, logger & helper utilities
├── scripts/
│   ├── start.sh                   # Linux/VPS startup script
│   └── test_api.py                # Automated endpoint tester
├── app.py                         # Main Application Entry Point
├── Dockerfile                     # Lightweight Docker image
├── docker-compose.yml             # Single-command deployment
├── requirements.txt               # Dependencies (Pure standard library)
├── BUG_BOUNTY_REPORT.md           # Full Penetration Test & Bug Bounty Audit Report
├── LICENSE                        # MIT License
└── README.md                      # Project Documentation
```

---

## 🔒 Security & Bug Bounty Audit

A comprehensive penetration test and vulnerability assessment was conducted on the upstream Denver69 JTV platform. The full executive report with CVE-style vulnerability breakdowns, PoCs, and remediations is available in [BUG_BOUNTY_REPORT.md](BUG_BOUNTY_REPORT.md).

---

## 👨‍💻 Developer & Credits

* **Developer:** **Kobir Shah**
* **Project:** JTV Pro Smart Engine
* **Contributions:** Open for Pull Requests and Issues on GitHub.

---

## ⚖️ Disclaimer

This project is created strictly for educational, research, and interoperability purposes. All channel logos, trademarks, and streaming content belong to their respective copyright owners.
