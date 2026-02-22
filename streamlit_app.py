"""
CROAudit — AI-powered landing page audit tool.
Run: streamlit run streamlit_app.py
"""

import math
import requests
import streamlit as st
from bs4 import BeautifulSoup

from extractor import extract_signals
from analyzer import analyze_with_claude

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CROAudit — AI Landing Page Audit",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Favicon + font + CSS ──────────────────────────────────────────────────────
FAVICON_SVG = (
    "data:image/svg+xml,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
    "<rect width='100' height='100' rx='22' fill='%234f46e5'/>"
    "<rect x='10' y='62' width='18' height='28' rx='5' fill='white' opacity='0.55'/>"
    "<rect x='41' y='42' width='18' height='48' rx='5' fill='white' opacity='0.78'/>"
    "<rect x='72' y='18' width='18' height='72' rx='5' fill='white'/>"
    "<polyline points='19,60 50,40 81,16' stroke='%23c7d2fe'"
    " stroke-width='6' fill='none' stroke-linecap='round' stroke-linejoin='round'/>"
    "</svg>"
)

st.markdown(
    f"""
<link rel="shortcut icon" href="{FAVICON_SVG}">
<link href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap" rel="stylesheet">
<style>

/* ── Base ─────────────────────────────────────────────── */
html, body, [class*="st-"], .stApp, p, span, div, label, h1, h2, h3 {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}
.stApp {{ background: #f1f5f9 !important; }}
.block-container {{ padding: 0 !important; max-width: 860px !important; margin: 0 auto; }}

/* Hide Streamlit chrome */
#MainMenu, footer, [data-testid="stHeader"],
.stDeployButton, [data-testid="stDecoration"],
[data-testid="stToolbar"] {{ display: none !important; }}

/* ── Inputs ───────────────────────────────────────────── */
.stTextInput input, .stTextArea textarea {{
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    color: #0f172a !important;
    transition: border-color .15s, box-shadow .15s !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,.12) !important;
    outline: none !important;
}}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {{
    color: #94a3b8 !important;
}}
.stSelectbox > div > div {{
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
    font-size: 14px !important;
}}
.stRadio label {{ font-size: 14px !important; }}
label[data-testid="stWidgetLabel"] p {{
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #374151 !important;
}}

/* ── Buttons ──────────────────────────────────────────── */
button[kind="primary"],
[data-testid="stFormSubmitButton"] button,
[data-testid="stBaseButton-primary"] {{
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    letter-spacing: .01em !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(79,70,229,.4) !important;
    transition: transform .15s, box-shadow .15s !important;
    padding: 10px 20px !important;
}}
button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] button:hover,
[data-testid="stBaseButton-primary"]:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(79,70,229,.5) !important;
}}
button[kind="secondary"],
[data-testid="stBaseButton-secondary"] {{
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    color: #374151 !important;
    background: #ffffff !important;
    transition: border-color .15s !important;
}}
button[kind="secondary"]:hover,
[data-testid="stBaseButton-secondary"]:hover {{
    border-color: #4f46e5 !important;
    color: #4f46e5 !important;
}}

/* ── Tabs ─────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 2px !important;
    background: #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border-bottom: none !important;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 9px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 7px 14px !important;
    color: #64748b !important;
    border: none !important;
    background: transparent !important;
}}
.stTabs [aria-selected="true"] {{
    background: #ffffff !important;
    color: #4f46e5 !important;
    font-weight: 700 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.12) !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    padding-top: 20px !important;
}}

/* ── Expanders ────────────────────────────────────────── */
[data-testid="stExpander"] {{
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 12px !important;
    margin-bottom: 10px !important;
    overflow: hidden !important;
    box-shadow: 0 1px 3px rgba(0,0,0,.05) !important;
}}
[data-testid="stExpander"] summary {{
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 14px 18px !important;
    background: #ffffff !important;
    color: #0f172a !important;
}}
[data-testid="stExpander"] summary:hover {{
    background: #f8fafc !important;
}}
[data-testid="stExpander"] > div > div {{
    padding: 0 18px 16px !important;
}}

/* ── Status widget ────────────────────────────────────── */
[data-testid="stStatus"] {{
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,.06) !important;
}}

/* ── Alerts ───────────────────────────────────────────── */
[data-testid="stAlert"] {{
    border-radius: 10px !important;
    font-size: 14px !important;
}}

/* ── Divider ──────────────────────────────────────────── */
hr {{ border-color: #e2e8f0 !important; margin: 24px 0 !important; }}

/* ── Toast ────────────────────────────────────────────── */
[data-testid="stToast"] {{ border-radius: 10px !important; }}

/* ── Custom component classes ─────────────────────────── */
.cro-card {{
    background: #ffffff;
    border-radius: 14px;
    border: 1.5px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,.05);
    padding: 20px 24px;
    margin-bottom: 16px;
}}
.badge {{
    display: inline-block; padding: 3px 10px; border-radius: 999px;
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: .04em; margin-right: 5px;
}}
.badge-critical {{ background:#fee2e2; color:#b91c1c; }}
.badge-high     {{ background:#ffedd5; color:#c2410c; }}
.badge-medium   {{ background:#fef9c3; color:#a16207; }}
.badge-low      {{ background:#f1f5f9; color:#475569; }}
.conf-high      {{ background:#dcfce7; color:#15803d; }}
.conf-medium    {{ background:#fef9c3; color:#a16207; }}
.conf-low       {{ background:#f1f5f9; color:#64748b; }}
.tag-headline        {{ background:#f3e8ff; color:#7e22ce; }}
.tag-subheadline     {{ background:#dbeafe; color:#1d4ed8; }}
.tag-cta             {{ background:#e0e7ff; color:#4338ca; }}
.tag-value-proposition {{ background:#ccfbf1; color:#0f766e; }}
.effort-low    {{ background:#dcfce7; color:#15803d; }}
.effort-medium {{ background:#fef9c3; color:#a16207; }}
.effort-high   {{ background:#fee2e2; color:#b91c1c; }}
.impact-low    {{ background:#f1f5f9; color:#475569; }}
.impact-medium {{ background:#dbeafe; color:#1d4ed8; }}
.impact-high   {{ background:#e0e7ff; color:#4338ca; }}
.quad-quick-win     {{ background:#16a34a; color:white; display:inline-block; padding:3px 10px; border-radius:999px; font-size:11px; font-weight:700; text-transform:uppercase; }}
.quad-major-project {{ background:#4f46e5; color:white; display:inline-block; padding:3px 10px; border-radius:999px; font-size:11px; font-weight:700; text-transform:uppercase; }}
.quad-schedule      {{ background:#d97706; color:white; display:inline-block; padding:3px 10px; border-radius:999px; font-size:11px; font-weight:700; text-transform:uppercase; }}
.quad-fill-in       {{ background:#64748b; color:white; display:inline-block; padding:3px 10px; border-radius:999px; font-size:11px; font-weight:700; text-transform:uppercase; }}
.evidence-box {{
    background:#f8fafc; border:1.5px solid #e2e8f0; border-radius:10px;
    padding:10px 14px; font-style:italic; color:#475569; font-size:13px;
    border-left:3px solid #4f46e5;
}}
.copy-before {{
    background:#fff1f2; border:1.5px solid #fecdd3; border-radius:10px;
    padding:14px 16px; font-size:14px; color:#374151; line-height:1.5;
}}
.copy-after {{
    background:#f0fdf4; border:1.5px solid #bbf7d0; border-radius:10px;
    padding:14px 16px; font-size:14px; color:#111827; font-weight:600;
    line-height:1.5;
}}
.sig-ok  {{ background:#dcfce7; color:#15803d; display:inline-block; padding:3px 10px; border-radius:999px; font-size:12px; font-weight:600; margin:3px; }}
.sig-bad {{ background:#fee2e2; color:#b91c1c; display:inline-block; padding:3px 10px; border-radius:999px; font-size:12px; font-weight:600; margin:3px; }}
.score-gauge {{ display:flex; flex-direction:column; align-items:center; gap:10px; }}
.score-band {{
    display:inline-block; padding:5px 16px; border-radius:999px;
    font-size:13px; font-weight:700; letter-spacing:.02em;
}}
.section-bar-row {{
    display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;
}}
.section-label {{
    font-weight:600; font-size:14px; color:#0f172a;
}}
.section-pill {{
    padding:3px 10px; border-radius:999px; font-size:11px; font-weight:700;
    text-transform:uppercase; letter-spacing:.04em;
}}

</style>
""",
    unsafe_allow_html=True,
)

# ── Constants ─────────────────────────────────────────────────────────────────
CONVERSION_GOALS = [
    "Generate leads (book a call / demo)",
    "Generate leads (get a quote)",
    "Generate leads (free trial signup)",
    "Collect emails / newsletter signup",
    "Webinar or event registration",
    "App download",
    "Ecommerce purchase",
    "Custom…",
]

TRAFFIC_SOURCES = {
    "Paid Search (Google / Bing)": "paid-search",
    "Paid Social (Meta / TikTok / LinkedIn)": "paid-social",
    "Email Campaign": "email",
    "Organic / SEO": "organic",
    "Referral (Blog / PR / Partner)": "referral",
}

INTENT_LEVELS = {
    "Cold — just discovered the brand": "cold",
    "Warm — comparing options": "warm",
    "Hot — ready to convert": "hot",
}

# Signals that a page is behind Cloudflare's bot protection
CF_SIGNALS = [
    "cloudflare", "cf-browser-verification", "just a moment",
    "ddos-guard", "ray id:", "checking your browser",
    "enable javascript and cookies", "please wait…",
]
# Signals that the page is a client-side SPA (JS renders the content)
SPA_SIGNALS = [
    "data-reactroot", "data-react-helmet", "__next", "_nuxt",
    "ng-version", "app-root", "ember-application",
]


# ── Helpers ───────────────────────────────────────────────────────────────────
def _score_color(score: int) -> str:
    if score < 40:  return "#dc2626"
    if score < 55:  return "#ea580c"
    if score < 70:  return "#d97706"
    if score < 85:  return "#16a34a"
    return "#059669"


def _band_style(score: int) -> str:
    if score < 40:  return "background:#fee2e2;color:#b91c1c;"
    if score < 55:  return "background:#ffedd5;color:#c2410c;"
    if score < 70:  return "background:#fef9c3;color:#a16207;"
    if score < 85:  return "background:#dcfce7;color:#15803d;"
    return "background:#d1fae5;color:#065f46;"


def _section_pill_style(label: str) -> str:
    return {
        "Poor":         "background:#fee2e2;color:#b91c1c;",
        "Below Average":"background:#ffedd5;color:#c2410c;",
        "Average":      "background:#fef9c3;color:#a16207;",
        "Good":         "background:#dcfce7;color:#15803d;",
        "Excellent":    "background:#d1fae5;color:#065f46;",
    }.get(label, "background:#f1f5f9;color:#475569;")


def render_score_gauge(score: int, band: str) -> str:
    r = 52
    circ = 2 * math.pi * r
    offset = circ * (1 - score / 100)
    fill = _score_color(score)
    band_s = _band_style(score)
    return f"""
<div class="score-gauge">
  <svg viewBox="0 0 140 140" width="170" height="170">
    <circle cx="70" cy="70" r="{r}" fill="none" stroke="#e2e8f0"
      stroke-width="13" transform="rotate(-90 70 70)"/>
    <circle cx="70" cy="70" r="{r}" fill="none" stroke="{fill}"
      stroke-width="13" stroke-linecap="round"
      stroke-dasharray="{circ:.2f}" stroke-dashoffset="{offset:.2f}"
      transform="rotate(-90 70 70)"/>
    <text x="70" y="64" text-anchor="middle" dominant-baseline="middle"
      font-family="Inter,sans-serif" font-size="34" font-weight="800"
      fill="#0f172a">{score}</text>
    <text x="70" y="85" text-anchor="middle" dominant-baseline="middle"
      font-family="Inter,sans-serif" font-size="13" fill="#94a3b8">/100</text>
  </svg>
  <span class="score-band" style="{band_s}">{band}</span>
</div>"""


def render_section_bar(name: str, score: int, max_score: int, label: str, findings: list) -> str:
    pct = round(score / max_score * 100)
    bar_color = _score_color(round(score / max_score * 100))
    pill_s = _section_pill_style(label)
    fi_html = "".join(
        f"<li style='color:#475569;font-size:13px;margin:4px 0;line-height:1.5;'>{f}</li>"
        for f in findings
    )
    return f"""
<div style="margin-bottom:16px;">
  <div class="section-bar-row">
    <span class="section-label">{name}</span>
    <div style="display:flex;align-items:center;gap:8px;">
      <span class="section-pill" style="{pill_s}">{label}</span>
      <span style="font-weight:700;color:#334155;font-size:15px;">
        {score}<span style="color:#94a3b8;font-weight:400;font-size:13px;">/{max_score}</span>
      </span>
    </div>
  </div>
  <div style="background:#e2e8f0;border-radius:999px;height:9px;">
    <div style="background:{bar_color};border-radius:999px;height:9px;width:{pct}%;
      transition:width .6s cubic-bezier(.4,0,.2,1);"></div>
  </div>
  {"<ul style='margin:10px 0 0;padding-left:18px;'>" + fi_html + "</ul>" if fi_html else ""}
</div>"""


def get_quad(impact: str, effort: str) -> tuple:
    if impact == "high"   and effort in ("low", "medium"): return "Quick Win",     "quad-quick-win"
    if impact == "high"   and effort == "high":            return "Major Project",  "quad-major-project"
    if impact == "medium" and effort in ("low", "medium"): return "Schedule",       "quad-schedule"
    if impact == "low"    and effort == "low":             return "Fill-In",        "quad-fill-in"
    return "Avoid", "quad-fill-in"


def detect_page_problem(html: str, body_text: str) -> str | None:
    """Return 'cloudflare', 'spa', 'empty', or None."""
    lower_head = html[:3000].lower()
    if any(s in lower_head for s in CF_SIGNALS):
        return "cloudflare"
    if len(body_text.strip()) < 400:
        if any(s in html for s in SPA_SIGNALS):
            return "spa"
        return "empty"
    return None


def fetch_page(url: str) -> tuple[str, str | None]:
    """
    Returns (html, error_message).
    error_message is None on success.
    """
    try:
        resp = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
            timeout=25,
            allow_redirects=True,
        )
    except requests.exceptions.Timeout:
        return "", "timeout"
    except requests.exceptions.ConnectionError:
        return "", "connection"
    except Exception as e:
        return "", f"error:{e}"

    if not resp.ok:
        return resp.text, f"http:{resp.status_code}"
    return resp.text, None


# ── Session state ─────────────────────────────────────────────────────────────
for key in ("report", "error", "page_warning"):
    if key not in st.session_state:
        st.session_state[key] = None


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="
    background: linear-gradient(140deg, #312e81 0%, #4f46e5 45%, #7c3aed 100%);
    border-radius: 0 0 28px 28px;
    padding: 36px 40px 44px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
">
  <!-- glow blobs -->
  <div style="position:absolute;top:-40px;right:-40px;width:200px;height:200px;
    background:rgba(167,139,250,.25);border-radius:50%;filter:blur(40px);"></div>
  <div style="position:absolute;bottom:-60px;left:60px;width:160px;height:160px;
    background:rgba(99,102,241,.3);border-radius:50%;filter:blur(50px);"></div>

  <div style="position:relative;display:flex;align-items:center;gap:18px;">
    <div style="
      background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);
      border-radius:16px;padding:14px;font-size:34px;line-height:1;
      backdrop-filter:blur(8px);flex-shrink:0;
    ">📊</div>
    <div>
      <div style="font-size:26px;font-weight:800;color:#ffffff;letter-spacing:-.4px;
        font-family:'Inter',sans-serif;">CROAudit</div>
      <div style="font-size:14px;color:rgba(255,255,255,.72);margin-top:3px;
        font-family:'Inter',sans-serif;">
        AI-powered landing page analysis &middot; Powered by Claude
      </div>
      <div style="display:flex;gap:16px;margin-top:12px;flex-wrap:wrap;">
        <span style="font-size:12px;color:rgba(255,255,255,.65);font-family:'Inter',sans-serif;">
          ✓ Signal extraction
        </span>
        <span style="font-size:12px;color:rgba(255,255,255,.65);font-family:'Inter',sans-serif;">
          ✓ Evidence-based recommendations
        </span>
        <span style="font-size:12px;color:rgba(255,255,255,.65);font-family:'Inter',sans-serif;">
          ✓ A/B test backlog
        </span>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  AUDIT FORM
# ══════════════════════════════════════════════════════════════════════════════
with st.container():
    st.markdown(
        '<div class="cro-card">',
        unsafe_allow_html=True,
    )

    tab_url, tab_html = st.tabs(["🌐  Audit a URL", "📋  Paste HTML"])

    with tab_url:
        url_input = st.text_input(
            "Landing page URL",
            placeholder="https://example.com/landing-page",
            key="url_input",
        )
        st.markdown(
            "<p style='font-size:12px;color:#94a3b8;margin:-8px 0 4px;'>"
            "Page must be publicly accessible. Pages behind Cloudflare or heavy JS frameworks "
            "(React, Next.js) may not render correctly — use the HTML tab instead."
            "</p>",
            unsafe_allow_html=True,
        )

    with tab_html:
        html_input = st.text_area(
            "Paste page HTML",
            height=160,
            placeholder=(
                "Chrome: right-click the page → View Page Source → Ctrl+A → Ctrl+C → paste here.\n"
                "For JS-rendered pages (React/Next.js): DevTools → Elements panel → "
                "right-click <html> → Copy → Copy outerHTML."
            ),
            key="html_input",
        )

    st.write("")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        goal_choice = st.selectbox("Conversion goal", CONVERSION_GOALS, key="goal")
    with col_b:
        source_label = st.selectbox("Traffic source", list(TRAFFIC_SOURCES.keys()), key="source")
    with col_c:
        intent_label = st.selectbox("Audience intent", list(INTENT_LEVELS.keys()), key="intent")

    custom_goal = ""
    if goal_choice == "Custom…":
        custom_goal = st.text_input("Describe your conversion goal", key="custom_goal")

    st.write("")
    submitted = st.button(
        "Run CRO Audit →",
        type="primary",
        use_container_width=True,
        key="submit_btn",
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PROCESS ON SUBMIT
# ══════════════════════════════════════════════════════════════════════════════
if submitted:
    url = (url_input or "").strip()
    html = (html_input or "").strip()
    final_goal = custom_goal.strip() if goal_choice == "Custom…" else goal_choice

    if not url and not html:
        st.error("Please provide a URL or paste the page HTML.")
        st.stop()
    if goal_choice == "Custom…" and not custom_goal.strip():
        st.error("Please describe your conversion goal.")
        st.stop()

    context = {
        "url": url or None,
        "conversion_goal": final_goal,
        "traffic_source": TRAFFIC_SOURCES[source_label],
        "audience_intent": INTENT_LEVELS[intent_label],
    }

    st.session_state.page_warning = None

    with st.status("Running audit…", expanded=True) as status:

        # ── Step 1: Get HTML ──────────────────────────────────────────────
        page_html = ""
        if url:
            st.write("🌐 Fetching page…")
            page_html, fetch_err = fetch_page(url)

            if fetch_err == "timeout":
                st.session_state.error = (
                    "**Request timed out** (25 s).\n\n"
                    "Open the page in Chrome → right-click → **View Page Source** → "
                    "select all → copy → paste in the **Paste HTML** tab."
                )
                st.session_state.report = None
                status.update(label="Fetch failed", state="error")
                st.stop()

            if fetch_err == "connection":
                st.session_state.error = (
                    "**Could not connect** to that URL.\n\n"
                    "Check the URL is correct and publicly accessible, "
                    "or paste the HTML directly."
                )
                st.session_state.report = None
                status.update(label="Connection error", state="error")
                st.stop()

            if fetch_err and fetch_err.startswith("http:"):
                code = fetch_err.split(":")[1]
                st.session_state.error = (
                    f"**HTTP {code}** — the server rejected the request.\n\n"
                    "This usually means the page is behind bot protection or requires a login. "
                    "Use the **Paste HTML** tab instead."
                )
                st.session_state.report = None
                status.update(label="HTTP error", state="error")
                st.stop()

            if fetch_err and fetch_err.startswith("error:"):
                st.session_state.error = f"Could not fetch page: {fetch_err[6:]}. Try pasting the HTML."
                st.session_state.report = None
                status.update(label="Fetch failed", state="error")
                st.stop()

            # Detect common page issues
            soup_check = BeautifulSoup(page_html, "lxml")
            body_check = soup_check.find("body")
            body_text_check = body_check.get_text(" ") if body_check else ""

            problem = detect_page_problem(page_html, body_text_check)

            if problem == "cloudflare":
                st.session_state.error = (
                    "**Cloudflare bot protection detected.**\n\n"
                    "Automated requests to this page are blocked. To audit it:\n\n"
                    "1. Open the URL in Chrome\n"
                    "2. Right-click anywhere → **View Page Source**\n"
                    "3. Select all (Ctrl+A / Cmd+A) → Copy\n"
                    "4. Paste into the **📋 Paste HTML** tab above\n\n"
                    "*Note: for JS-rendered pages (React/Next.js), use DevTools → Elements → "
                    "right-click `<html>` → Copy → Copy outerHTML instead.*"
                )
                st.session_state.report = None
                status.update(label="Blocked by Cloudflare", state="error")
                st.stop()

            if problem in ("spa", "empty"):
                # Don't fail hard — but warn and proceed with what we have
                st.session_state.page_warning = (
                    "⚠️ **Minimal content detected.** This page may be rendered by JavaScript "
                    "(React / Next.js / Vue). The audit ran on the server-rendered HTML shell, "
                    "which may lack your actual headlines, CTAs, and copy.\n\n"
                    "For best results: in Chrome, open DevTools (F12) → **Elements** tab → "
                    "right-click the `<html>` element → **Copy** → **Copy outerHTML**, "
                    "then paste in the **📋 Paste HTML** tab."
                )
        else:
            page_html = html

        if len(page_html.strip()) < 80:
            st.session_state.error = "Page content appears empty. Please check the URL or paste the HTML."
            st.session_state.report = None
            status.update(label="Empty content", state="error")
            st.stop()

        # ── Step 2: Extract signals ───────────────────────────────────────
        st.write("🔍 Extracting CRO signals…")
        try:
            signals = extract_signals(page_html, url)
        except Exception as e:
            st.session_state.error = f"Signal extraction failed: {e}"
            st.session_state.report = None
            status.update(label="Extraction failed", state="error")
            st.stop()

        # ── Step 3: AI analysis ───────────────────────────────────────────
        st.write("🤖 Analysing with Claude…")
        try:
            analysis = analyze_with_claude(signals, context)
        except Exception as e:
            st.session_state.error = f"AI analysis failed: {e}"
            st.session_state.report = None
            status.update(label="Analysis failed", state="error")
            st.stop()

        from datetime import datetime, timezone
        st.session_state.report = {
            **analysis,
            "signals": signals,
            "context": context,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        st.session_state.error = None
        status.update(label="Audit complete!", state="complete", expanded=False)


# ── Show error ────────────────────────────────────────────────────────────────
if st.session_state.error:
    st.error(st.session_state.error)


# ══════════════════════════════════════════════════════════════════════════════
#  RESULTS
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.report:
    report  = st.session_state.report
    ctx     = report["context"]
    signals = report["signals"]
    score   = report["overallScore"]
    band    = report["scoreBand"]

    if st.session_state.page_warning:
        st.warning(st.session_state.page_warning)

    st.write("")

    # ── Context strip ─────────────────────────────────────────────────────
    source_display = {v: k for k, v in TRAFFIC_SOURCES.items()}.get(
        ctx["traffic_source"], ctx["traffic_source"]
    )
    intent_short = ctx["audience_intent"].capitalize()

    parts = []
    if ctx.get("url"):
        u = ctx["url"]
        parts.append(f"🌐 {u[:55]}{'…' if len(u)>55 else ''}")
    parts += [
        f"🎯 {ctx['conversion_goal']}",
        f"📡 {source_display}",
        f"👤 {intent_short} intent",
    ]
    tags_html = " &nbsp;".join(
        f"<span style='background:#e0e7ff;color:#3730a3;padding:4px 12px;"
        f"border-radius:999px;font-size:12px;font-weight:600;"
        f"font-family:Inter,sans-serif;'>{p}</span>"
        for p in parts
    )
    st.markdown(tags_html, unsafe_allow_html=True)
    st.write("")

    # ── Score + Summary ───────────────────────────────────────────────────
    st.markdown('<div class="cro-card">', unsafe_allow_html=True)

    col_gauge, col_sum = st.columns([1, 3], gap="large")
    with col_gauge:
        st.markdown(render_score_gauge(score, band), unsafe_allow_html=True)
    with col_sum:
        st.markdown(
            f"<p style='font-size:11px;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:.08em;color:#94a3b8;margin-bottom:6px;'>"
            f"EXECUTIVE SUMMARY</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='font-size:15px;line-height:1.65;color:#1e293b;"
            f"font-family:Inter,sans-serif;margin:0;'>{report.get('summary','')}</p>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    # ── Tabs ─────────────────────────────────────────────────────────────
    tab_s, tab_r, tab_c, tab_e, tab_sig = st.tabs([
        "📊 Section Scores",
        "🔥 Recommendations",
        "✍️ Copy Lab",
        "🧪 Experiments",
        "🔍 Raw Signals",
    ])

    # ── Section Scores ────────────────────────────────────────────────────
    with tab_s:
        for sec in report.get("sectionScores", []):
            st.markdown(
                render_section_bar(
                    sec["name"], sec["score"], sec["maxScore"],
                    sec["label"], sec.get("findings", []),
                ),
                unsafe_allow_html=True,
            )

    # ── Recommendations ───────────────────────────────────────────────────
    with tab_r:
        recs = report.get("topRecommendations", [])
        if not recs:
            st.info("No recommendations returned.")
        for i, rec in enumerate(recs):
            pri  = rec.get("priority", "low")
            conf = rec.get("confidence", "medium")
            with st.expander(rec.get("issue", "Recommendation"), expanded=(i == 0)):
                st.markdown(
                    f'<span class="badge badge-{pri}">{pri}</span>'
                    f'<span class="badge conf-{conf}">{conf} confidence</span>'
                    f'<span style="font-size:12px;color:#94a3b8;font-weight:600;">'
                    f'{rec.get("category","")}</span>',
                    unsafe_allow_html=True,
                )
                st.write("")
                st.markdown(
                    f"<p style='font-size:14px;line-height:1.6;color:#1e293b;margin:0;'>"
                    f"{rec.get('suggestion','')}</p>",
                    unsafe_allow_html=True,
                )
                if rec.get("evidence"):
                    st.write("")
                    st.markdown(
                        f'<div class="evidence-box">"{rec["evidence"]}"</div>',
                        unsafe_allow_html=True,
                    )
                if rec.get("hypothesis"):
                    st.write("")
                    st.markdown(
                        f"<p style='font-size:13px;color:#475569;font-style:italic;"
                        f"margin:0;'>💡 {rec['hypothesis']}</p>",
                        unsafe_allow_html=True,
                    )
                if rec.get("expectedImpact"):
                    st.success(f"Expected impact: {rec['expectedImpact']}", icon="📈")

    # ── Copy Lab ──────────────────────────────────────────────────────────
    with tab_c:
        rewrites = report.get("copyRewrites", [])
        if not rewrites:
            st.info("No copy rewrites returned.")
        for idx, rw in enumerate(rewrites):
            rw_type  = rw.get("type", "")
            tag_cls  = {
                "headline":          "tag-headline",
                "subheadline":       "tag-subheadline",
                "cta":               "tag-cta",
                "value-proposition": "tag-value-proposition",
            }.get(rw_type, "tag-cta")
            type_label = rw_type.replace("-", " ").title()

            st.markdown(
                f'<span class="badge {tag_cls}">{type_label}</span>',
                unsafe_allow_html=True,
            )
            col_b, col_a = st.columns(2, gap="medium")
            with col_b:
                st.markdown(
                    "<p style='font-size:11px;font-weight:700;text-transform:uppercase;"
                    "letter-spacing:.06em;color:#dc2626;margin-bottom:6px;'>Before</p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="copy-before">{rw.get("original") or "<em>Not detected</em>"}</div>',
                    unsafe_allow_html=True,
                )
            with col_a:
                st.markdown(
                    "<p style='font-size:11px;font-weight:700;text-transform:uppercase;"
                    "letter-spacing:.06em;color:#16a34a;margin-bottom:6px;'>After</p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="copy-after">{rw.get("rewritten","")}</div>',
                    unsafe_allow_html=True,
                )
                if st.button("📋 Copy", key=f"cpbtn_{idx}", use_container_width=False):
                    st.toast(f"Copied rewrite!")

            if rw.get("rationale"):
                st.markdown(
                    f"<p style='font-size:13px;color:#64748b;margin:6px 0 0;"
                    f"font-style:italic;'>ℹ️ {rw['rationale']}</p>",
                    unsafe_allow_html=True,
                )
            st.write("")

    # ── Experiments ───────────────────────────────────────────────────────
    with tab_e:
        experiments = report.get("experimentIdeas", [])
        if not experiments:
            st.info("No experiment ideas returned.")
        for exp in experiments:
            impact = exp.get("impactLevel", "medium")
            effort = exp.get("effortLevel", "medium")
            ql, qc = get_quad(impact, effort)
            with st.expander(exp.get("name", "Experiment")):
                st.markdown(
                    f'<span class="{qc}">{ql}</span>&nbsp;&nbsp;'
                    f'<span class="badge effort-{effort}">Effort: {effort}</span>'
                    f'<span class="badge impact-{impact}">Impact: {impact}</span>',
                    unsafe_allow_html=True,
                )
                st.write("")
                st.markdown(
                    f"<p style='font-size:13px;color:#475569;font-style:italic;margin:0;'>"
                    f"💡 {exp.get('hypothesis','')}</p>",
                    unsafe_allow_html=True,
                )
                st.write("")
                st.markdown(f"**Variant:** {exp.get('variant','')}")
                st.markdown(f"**Primary metric:** `{exp.get('primaryMetric','')}`")
                guards = exp.get("guardrailMetrics", [])
                if guards:
                    st.markdown(f"**Guardrails:** {' · '.join(guards)}")

    # ── Raw Signals ───────────────────────────────────────────────────────
    with tab_sig:
        st.markdown('<div class="cro-card">', unsafe_allow_html=True)
        st.markdown(
            "<p style='font-size:11px;font-weight:700;text-transform:uppercase;"
            "letter-spacing:.08em;color:#94a3b8;margin-bottom:12px;'>PAGE STRUCTURE</p>",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Title:** {signals['page_title'] or '*none*'}")
            st.markdown(f"**H1:** {signals['h1'] or '*⚠️ none detected*'}")
        with c2:
            st.markdown(f"**Nav links:** {signals['nav_links']}")
            st.markdown(f"**Outbound links:** {signals['outbound_links']}")
        if signals["h2s"]:
            st.markdown("**H2 subheadings:**")
            for h in signals["h2s"][:6]:
                st.markdown(f"- {h}")

        st.markdown("---")
        st.markdown("**CTAs detected**")
        if signals["cta_buttons"]:
            for c in signals["cta_buttons"]:
                st.markdown(f'- `"{c["text"]}"` [{c["type"]}]')
        else:
            st.warning("No CTAs detected.")

        st.markdown("---")
        st.markdown("**Form fields**")
        ff = signals["form_fields"]
        if ff:
            req = sum(1 for f in ff if f["required"])
            st.markdown(f"{len(ff)} total · {req} required")
            for f in ff:
                lbl = f["label"] or f["name"] or f["type"]
                st.markdown(f'- `{lbl}` {"*(required)*" if f["required"] else ""}')
        else:
            st.markdown("*No form detected*")

        st.markdown("---")
        st.markdown("**Trust signals**")
        ts = signals["trust_signals"]
        checks = [
            ("Testimonials", ts["has_testimonials"]),
            ("Star Ratings", ts["has_star_ratings"]),
            ("Logo Strip", ts["has_logo_strip"]),
            ("Money-back Guarantee", ts["has_money_back_guarantee"]),
            ("Social Proof Numbers", ts["has_social_proof"]),
            ("Security Badges", ts["has_security_badges"]),
        ]
        st.markdown(
            " ".join(
                f'<span class="{"sig-ok" if ok else "sig-bad"}">{"✓" if ok else "✗"} {lbl}</span>'
                for lbl, ok in checks
            ),
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("**Specificity signals**")
        sp = signals["specificity_signals"]
        sp_checks = [
            ("Numbers", sp["has_numbers"]),
            ("Percentages", sp["has_percentages"]),
            ("Timeframes", sp["has_timeframes"]),
            ("Guarantees", sp["has_guarantees"]),
        ]
        st.markdown(
            " ".join(
                f'<span class="{"sig-ok" if ok else "sig-bad"}">{"✓" if ok else "✗"} {lbl}</span>'
                for lbl, ok in sp_checks
            ),
            unsafe_allow_html=True,
        )
        if sp["examples"]:
            st.caption(f"Examples: {', '.join(sp['examples'])}")

        st.markdown("---")
        rl = signals["reading_level"]
        st.markdown(
            f"**Reading level:** Grade {rl['estimated_grade']} · "
            f"{rl['avg_sentence_length']} words/sentence · "
            f"{rl['avg_word_length']} chars/word"
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown('<div style="display:flex;justify-content:space-between;align-items:center;">', unsafe_allow_html=True)
    col_new, col_tip = st.columns([1, 2])
    with col_new:
        if st.button("＋ New audit", key="reset"):
            st.session_state.report = None
            st.session_state.error  = None
            st.session_state.page_warning = None
            st.rerun()
    with col_tip:
        st.markdown(
            "<p style='color:#94a3b8;font-size:12px;text-align:right;margin:0;padding-top:10px;'>"
            "Ctrl+P / Cmd+P to save as PDF</p>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
