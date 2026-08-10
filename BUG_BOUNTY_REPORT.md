# 🛡️ Denver69 JTV Platform — Deep Bug Bounty & Security Audit Report

**Target:** `https://game.denver69.fun/Jtv/`  
**Audit Scope:** Authentication, Authorization (IDOR), Business Logic, DRM Licensing, Information Disclosure, Rate Limiting  
**Lead Security Researcher:** **Kobir Shah**  
**Classification:** #1 Pro Bug Bounty Assessment  
**Date:** 11 August 2026  

---

## 📊 Executive Vulnerability Summary

| Bug ID | Vulnerability Title | Severity (CVSS v3.1) | Status | Impact Area |
| :--- | :--- | :--- | :--- | :--- |
| **VULN-01** | Unauthenticated IDOR in Token Management Panels | 🔴 **HIGH (7.5)** | **Confirmed** | IP Manager, Addon Manager, Channel Customizer |
| **VULN-02** | Static Secret Key Business Logic Flaw (+10 Days VIP) | 🟠 **MEDIUM-HIGH (6.8)** | **Confirmed** | Token Validity Extension Endpoint |
| **VULN-03** | DRM ClearKey Server User-Agent Spoofing Bypass | 🟡 **MEDIUM (5.3)** | **Confirmed** | `key.php` License Decryption API |
| **VULN-04** | Sensitive Channel Architecture & Source Disclosure | 🟡 **MEDIUM (5.3)** | **Confirmed** | `Customised_{token}` Inline Script |
| **VULN-05** | Lack of Rate-Limiting on 4-Digit OTP & Token API | 🔵 **LOW-MEDIUM (4.8)**| **Confirmed** | Promo & Token Generation Endpoints |

---

## 🔍 Detailed Vulnerability Breakdown & Proof of Concept (PoC)

---

### 🔴 VULN-01: Insecure Direct Object Reference (IDOR) on Management Panels
* **Affected Endpoints:**
  * `https://game.denver69.fun/Jtv/Token_{TOKEN}` *(IP Manager)*
  * `https://game.denver69.fun/Jtv/Edit_{TOKEN}` *(Addon Manager)*
  * `https://game.denver69.fun/Jtv/Customised_{TOKEN}` *(Channel Customizer)*
* **Vulnerability Description:**
  The server relies solely on a 6-character alphanumeric token ID (`{TOKEN}`) to authenticate users to sensitive management dashboards. There is zero session token verification or secondary authentication.
* **Security Impact:**
  Any attacker who discovers or brute-forces another user's 6-character token can view active IP addresses, add/remove authorization for IP addresses, inject arbitrary stream URLs via the Addon Manager, or modify/reset channel configurations.
* **Proof of Concept (PoC):**
  ```bash
  # Accessible from any external IP without authentication:
  curl -s -H "User-Agent: Mozilla/5.0" "https://game.denver69.fun/Jtv/Token_Ei4Uus"
  ```

---

### 🟠 VULN-02: Static Secret Promo Key Flaw (+10 Days / 240 Hours Extension)
* **Affected Endpoint:**
  * `https://game.denver69.fun/Jtv/index.php?e=16fa4fd95b8badd6df7c5e6532b9101106`
* **Vulnerability Description:**
  The `e=16fa4fd95b8badd6df7c5e6532b9101106` parameter is a hardcoded, non-expiring secret trigger. Sending a single GET request with an active session cookie automatically extends the token expiration timestamp from 6 hours to **10 Days (+240 Hours)**.
* **Security Impact:**
  Allows arbitrary users to bypass standard token expiry limits and obtain persistent VIP access without authorization or payment.
* **Proof of Concept (PoC):**
  ```python
  # 1. Generate token (Expiry: 6h / billed-till: 1786390355)
  # 2. Trigger secret extension:
  urllib.request.urlopen("https://game.denver69.fun/Jtv/index.php?e=16fa4fd95b8badd6df7c5e6532b9101106")
  # 3. New Expiry: 10 Days (+864,000s / billed-till: 1787254355)
  ```

---

### 🟡 VULN-03: DRM ClearKey Security Bypass via User-Agent Spoofing
* **Affected Endpoint:**
  * `https://game.denver69.fun/Jtv/key.php?id={channel_id}&token={token}`
* **Vulnerability Description:**
  The server attempts to prevent scraping by returning a fake `404 Error - Page is Secured` HTML page when accessed by standard browser User-Agents. However, it blindly trusts client-provided headers like `User-Agent: Denver1769` or `TiviMate`.
* **Security Impact:**
  Allows automated scripts and unauthorized clients to decrypt and extract raw Base64 ClearKey values for all 1,694+ channels.
* **Proof of Concept (PoC):**
  ```bash
  # Standard browser blocked (404 Page):
  curl -s "https://game.denver69.fun/Jtv/key.php?id=143&token=Ei4Uus"
  
  # User-Agent Spoofing reveals full Base64 ClearKeys (200 OK):
  curl -s -H "User-Agent: Denver1769" "https://game.denver69.fun/Jtv/key.php?id=143&token=Ei4Uus"
  ```

---

### 🟡 VULN-04: Sensitive Full Architecture Disclosure via Inline JavaScript
* **Affected Endpoint:**
  * `https://game.denver69.fun/Jtv/Customised_{TOKEN}`
* **Vulnerability Description:**
  The page embeds an entire unauthenticated JSON channel tree (213 KB) in client-side JavaScript (`const data = {...}`).
* **Security Impact:**
  Enables competitors and automated scrapers to clone the complete channel mapping, internal IDs, and CDN routing in a single request.

---

### 🔵 VULN-05: Lack of Rate Limiting on 4-Digit OTP Promo System
* **Affected Endpoint:**
  * `POST /Jtv/index.php` (`otp_code` & `extend_by_code`)
* **Vulnerability Description:**
  The 4-digit promo code field (0000 to 9999) has no rate-limiting, IP throttling, or CAPTCHA.
* **Security Impact:**
  A multi-threaded script can brute-force all 10,000 combinations in under 2 minutes.

---

## 🛠️ Remediation & Patch Recommendations

1. **Fix IDOR on Management Panels:** Enforce mandatory session tokens and password authentication on `/Token_`, `/Edit_`, and `/Customised_`.
2. **Revoke Static Extension Key:** Invalidate `e=16fa4fd95b8badd6df7c5e6532b9101106` and implement signed, time-limited, one-time-use cryptographic tokens.
3. **Implement Robust DRM Authorization:** Validate session integrity on `/key.php` instead of relying on spoofable User-Agent strings.
4. **Deploy Rate Limiting & CAPTCHA:** Add Cloudflare Turnstile CAPTCHA and per-IP rate limits on promo code submissions.

---
**Report compiled by Kobir Shah**
