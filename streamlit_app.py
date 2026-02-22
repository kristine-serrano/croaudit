"""
CROAudit — AI-powered landing page audit tool.
Main entry point: streamlit run streamlit_app.py
"""

import math
import requests
import streamlit as st

from extractor import extract_signals
from analyzer import analyze_with_claude

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CROAudit — AI Landing Page Audit",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global */
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 900px; }
h1 { font-weight: 800 !important; }

/* Score gauge */
.score-gauge-wrapper { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.score-band-pill {
    display: inline-block; padding: 4px 14px; border-radius: 999px;
    font-size: 13px; font-weight: 600;
}

/* Priority badges */
.badge {
    display: inline-block; padding: 2px 10px; border-radius: 999px;
    font-size: 12px; font-weight: 700; margin-right: 6px;
}
.badge-critical { background: #fee2e2; color: #b91c1c; }
.badge-high     { background: #ffedd5; color: #c2410c; }
.badge-medium   { background: #fef9c3; color: #a16207; }
.badge-low      { background: #f1f5f9; color: #475569; }

/* Confidence */
.conf-high   { background: #dcfce7; color: #15803d; }
.conf-medium { background: #fef9c3; color: #a16207; }
.conf-low    { background: #f1f5f9; color: #64748b; }

/* Type tags */
.tag-headline       { background: #f3e8ff; color: #7e22ce; }
.tag-subheadline    { background: #dbeafe; color: #1d4ed8; }
.tag-cta            { background: #e0e7ff; color: #4338ca; }
.tag-value-proposition { background: #ccfbf1; color: #0f766e; }

/* Effort / Impact */
.effort-low    { background: #dcfce7; color: #15803d; }
.effort-medium { background: #fef9c3; color: #a16207; }
.effort-high   { background: #fee2e2; color: #b91c1c; }
.impact-low    { background: #f1f5f9; color: #475569; }
.impact-medium { background: #dbeafe; color: #1d4ed8; }
.impact-high   { background: #e0e7ff; color: #4338ca; }

/* Quad label */
.quad-quick-win     { background: #16a34a; color: white; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.quad-major-project { background: #4f46e5; color: white; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.quad-schedule      { background: #d97706; color: white; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.quad-fill-in       { background: #64748b; color: white; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.quad-avoid         { background: #dc2626; color: white; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }

/* Evidence box */
.evidence-box {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 8px; padding: 10px 14px;
    font-style: italic; color: #475569; font-size: 13px;
    margin: 4px 0;
}

/* Copy panel */
.copy-original {
    background: #fff1f2; border: 1px solid #fecdd3;
    border-radius: 8px; padding: 10px 14px; font-size: 14px; color: #374151;
}
.copy-rewritten {
    background: #f0fdf4; border: 1px solid #bbf7d0;
    border-radius: 8px; padding: 10px 14px; font-size: 14px; color: #111827; font-weight: 600;
}

/* Signal badges */
.sig-ok  { background: #dcfce7; color: #15803d; display:inline-block; padding:2px 9px; border-radius:999px; font-size:12px; font-weight:600; margin:2px; }
.sig-bad { background: #fee2e2; color: #b91c1c; display:inline-block; padding:2px 9px; border-radius:999px; font-size:12px; font-weight:600; margin:2px; }
</style>
""", unsafe_allow_html=True)


# ── Constants ─────────────────────────────────────────────────────────────────
CONVERSION_GOALS = [
    "Generate leads (book a call)",
    "Generate leads (get a quote)",
    "Generate leads (free trial signup)",
    "Collect emails / newsletter signup",
    "Webinar or event registration",
    "App download",
    "Ecommerce purchase",
    "Custom…",
]

TRAFFIC_SOURCES = {
    "Paid Search (Google/Bing)": "paid-search",
    "Paid Social (Meta/TikTok/LinkedIn)": "paid-social",
    "Email Campaign": "email",
    "Organic / SEO": "organic",
    "Referral (Blog/PR/Partner)": "referral",
}

INTENT_LEVELS = {
    "Cold — just discovered the brand": "cold",
    "Warm — solution-aware, comparing options": "warm",
    "Hot — high intent, ready to convert": "hot",
}

SCORE_COLORS = {
    "fill": lambda s: (
        "#dc2626" if s < 40 else
        "#ea580c" if s < 55 else
        "#d97706" if s < 70 else
        "#16a34a" if s < 85 else
        "#059669"
    ),
    "band_style": lambda s: (
        "background:#fee2e2;color:#b91c1c;" if s < 40 else
        "background:#ffedd5;color:#c2410c;" if s < 55 else
        "background:#fef9c3;color:#a16207;" if s < 70 else
        "background:#dcfce7;color:#15803d;" if s < 85 else
        "background:#d1fae5;color:#065f46;"
    ),
}


# ── Helper: SVG score gauge ──────────────────────────────────────────────────
def render_score_gauge(score: int, band: str) -> str:
    radius = 54
    circumference = 2 * math.pi * radius
    offset = circumference * (1 - score / 100)
    fill = SCORE_COLORS["fill"](score)
    band_style = SCORE_COLORS["band_style"](score)

    return f"""
<div class="score-gauge-wrapper">
  <svg viewBox="0 0 140 140" width="160" height="160">
    <circle cx="70" cy="70" r="{radius}" fill="none" stroke="#e2e8f0"
      stroke-width="12" transform="rotate(-90 70 70)"/>
    <circle cx="70" cy="70" r="{radius}" fill="none" stroke="{fill}"
      stroke-width="12" stroke-linecap="round"
      stroke-dasharray="{circumference:.2f}"
      stroke-dashoffset="{offset:.2f}"
      transform="rotate(-90 70 70)"/>
    <text x="70" y="66" text-anchor="middle" dominant-baseline="middle"
      font-size="30" font-weight="800" fill="#0f172a">{score}</text>
    <text x="70" y="88" text-anchor="middle" dominant-baseline="middle"
      font-size="12" fill="#94a3b8">/100</text>
  </svg>
  <span class="score-band-pill" style="{band_style}">{band}</span>
</div>
"""


# ── Helper: progress bar ──────────────────────────────────────────────────────
def score_bar_color(score: int, max_score: int) -> str:
    pct = score / max_score
    if pct < 0.4:  return "#dc2626"
    if pct < 0.55: return "#ea580c"
    if pct < 0.7:  return "#d97706"
    if pct < 0.85: return "#16a34a"
    return "#059669"


def render_section_bar(name: str, score: int, max_score: int, label: str, findings: list) -> str:
    pct = round(score / max_score * 100)
    color = score_bar_color(score, max_score)
    label_styles = {
        "Poor": "background:#fee2e2;color:#b91c1c;",
        "Below Average": "background:#ffedd5;color:#c2410c;",
        "Average": "background:#fef9c3;color:#a16207;",
        "Good": "background:#dcfce7;color:#15803d;",
        "Excellent": "background:#d1fae5;color:#065f46;",
    }
    ls = label_styles.get(label, "background:#f1f5f9;color:#475569;")
    findings_html = "".join(f"<li style='color:#475569;font-size:13px;margin:3px 0;'>{f}</li>" for f in findings)

    return f"""
<div style="margin-bottom:12px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">
    <span style="font-weight:600;font-size:14px;color:#0f172a;">{name}</span>
    <div style="display:flex;align-items:center;gap:8px;">
      <span style="padding:2px 10px;border-radius:999px;font-size:12px;font-weight:600;{ls}">{label}</span>
      <span style="font-weight:700;color:#334155;font-size:14px;">{score}<span style="color:#94a3b8;font-weight:400;">/{max_score}</span></span>
    </div>
  </div>
  <div style="background:#e2e8f0;border-radius:999px;height:8px;width:100%;">
    <div style="background:{color};border-radius:999px;height:8px;width:{pct}%;transition:width 0.7s;"></div>
  </div>
  {'<ul style="margin-top:8px;padding-left:16px;">' + findings_html + "</ul>" if findings else ""}
</div>
"""


# ── Helper: quadrant label ───────────────────────────────────────────────────
def get_quad(impact: str, effort: str) -> tuple:
    if impact == "high" and effort == "low":    return "Quick Win", "quad-quick-win"
    if impact == "high" and effort == "medium": return "Quick Win", "quad-quick-win"
    if impact == "high" and effort == "high":   return "Major Project", "quad-major-project"
    if impact == "medium" and effort == "low":  return "Fill-In", "quad-fill-in"
    if impact == "medium" and effort == "medium": return "Schedule", "quad-schedule"
    if impact == "medium" and effort == "high":   return "Schedule", "quad-schedule"
    if impact == "low" and effort == "low":     return "Fill-In", "quad-fill-in"
    return "Avoid", "quad-avoid"


# ── Session state ─────────────────────────────────────────────────────────────
if "report" not in st.session_state:
    st.session_state.report = None
if "error" not in st.session_state:
    st.session_state.error = None


# ── Header ────────────────────────────────────────────────────────────────────
col_logo, col_badge = st.columns([6, 1])
with col_logo:
    st.markdown(
        "<h1 style='margin-bottom:0;font-size:2rem;'>📊 CROAudit</h1>",
        unsafe_allow_html=True,
    )
    st.caption("AI-powered landing page analysis · Powered by Claude")
with col_badge:
    st.markdown(
        "<div style='text-align:right;padding-top:12px;'>"
        "<span style='background:#e0e7ff;color:#4338ca;padding:4px 12px;border-radius:999px;"
        "font-size:12px;font-weight:700;'>MVP</span></div>",
        unsafe_allow_html=True,
    )

st.divider()


# ── Audit form ────────────────────────────────────────────────────────────────
with st.expander("**Audit settings**", expanded=(st.session_state.report is None)):
    tab_url, tab_html = st.tabs(["🌐 Audit a URL", "📋 Paste HTML"])

    with tab_url:
        url_input = st.text_input(
            "Landing page URL",
            placeholder="https://example.com/landing-page",
            key="url_input",
        )
        st.caption("Page must be publicly accessible. If protected by Cloudflare, use the HTML tab.")

    with tab_html:
        html_input = st.text_area(
            "Paste page HTML",
            height=180,
            placeholder="Right-click → View Page Source → Ctrl+A → paste here…",
            key="html_input",
        )

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        goal_choice = st.selectbox("Conversion goal", CONVERSION_GOALS, key="goal")
        if goal_choice == "Custom…":
            custom_goal = st.text_input("Describe your goal", key="custom_goal")
        else:
            custom_goal = ""

    with col_b:
        source_label = st.selectbox("Traffic source", list(TRAFFIC_SOURCES.keys()), key="source")

    with col_c:
        intent_label = st.selectbox("Audience intent", list(INTENT_LEVELS.keys()), key="intent")

    submitted = st.button(
        "Run CRO Audit →",
        type="primary",
        use_container_width=True,
        key="submit_btn",
    )


# ── Run audit on submit ───────────────────────────────────────────────────────
if submitted:
    url = url_input.strip()
    html = html_input.strip()
    final_goal = custom_goal.strip() if goal_choice == "Custom…" else goal_choice

    # Validate inputs
    if not url and not html:
        st.error("Please provide a URL or paste the page HTML.")
        st.stop()
    if not final_goal:
        st.error("Please describe your conversion goal.")
        st.stop()

    context = {
        "url": url or None,
        "conversion_goal": final_goal,
        "traffic_source": TRAFFIC_SOURCES[source_label],
        "audience_intent": INTENT_LEVELS[intent_label],
    }

    with st.status("Running audit…", expanded=True) as status:
        # Step 1: Fetch page
        page_html = ""
        if url:
            st.write("Fetching page content…")
            try:
                resp = requests.get(
                    url,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (compatible; CROAuditBot/1.0; "
                            "+https://croaudit.app)"
                        ),
                        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
                    },
                    timeout=30,
                    allow_redirects=True,
                )
                if not resp.ok:
                    st.session_state.error = (
                        f"Page returned HTTP {resp.status_code}. "
                        "Try the HTML paste option instead."
                    )
                    st.session_state.report = None
                    status.update(label="Failed", state="error")
                    st.stop()
                page_html = resp.text
            except requests.exceptions.Timeout:
                st.session_state.error = "Request timed out (30s). Try pasting the HTML."
                st.session_state.report = None
                status.update(label="Failed", state="error")
                st.stop()
            except Exception as e:
                st.session_state.error = f"Could not fetch URL: {e}. Try pasting the HTML."
                st.session_state.report = None
                status.update(label="Failed", state="error")
                st.stop()
        else:
            page_html = html

        if len(page_html) < 100:
            st.session_state.error = "Page content is too short to audit."
            st.session_state.report = None
            status.update(label="Failed", state="error")
            st.stop()

        # Step 2: Extract signals
        st.write("Extracting CRO signals…")
        try:
            signals = extract_signals(page_html, url)
        except Exception as e:
            st.session_state.error = f"Signal extraction failed: {e}"
            st.session_state.report = None
            status.update(label="Failed", state="error")
            st.stop()

        # Step 3: Analyze with Claude
        st.write("Running AI analysis with Claude…")
        try:
            analysis = analyze_with_claude(signals, context)
        except Exception as e:
            st.session_state.error = f"AI analysis failed: {e}"
            st.session_state.report = None
            status.update(label="Failed", state="error")
            st.stop()

        # Build final report
        from datetime import datetime, timezone
        st.session_state.report = {
            **analysis,
            "signals": signals,
            "context": context,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        st.session_state.error = None
        status.update(label="Audit complete!", state="complete")


# ── Show error ────────────────────────────────────────────────────────────────
if st.session_state.error:
    st.error(st.session_state.error)


# ── Render report ─────────────────────────────────────────────────────────────
if st.session_state.report:
    report = st.session_state.report
    ctx = report["context"]
    signals = report["signals"]

    st.divider()

    # Context bar
    source_display = {v: k for k, v in TRAFFIC_SOURCES.items()}.get(ctx["traffic_source"], ctx["traffic_source"])
    intent_display = ctx["audience_intent"].capitalize()

    ctx_tags = " &nbsp;".join([
        f"<span style='background:#f1f5f9;color:#475569;padding:3px 12px;border-radius:999px;font-size:13px;'>🎯 {ctx['conversion_goal']}</span>",
        f"<span style='background:#f1f5f9;color:#475569;padding:3px 12px;border-radius:999px;font-size:13px;'>📡 {source_display}</span>",
        f"<span style='background:#f1f5f9;color:#475569;padding:3px 12px;border-radius:999px;font-size:13px;'>🎯 {intent_display} intent</span>",
    ])
    if ctx.get("url"):
        ctx_tags = f"<span style='background:#f1f5f9;color:#475569;padding:3px 12px;border-radius:999px;font-size:13px;'>🌐 {ctx['url'][:60]}{'…' if len(ctx['url'])>60 else ''}</span> &nbsp;" + ctx_tags
    st.markdown(ctx_tags, unsafe_allow_html=True)
    st.write("")

    # Score + Summary
    col_score, col_summary = st.columns([1, 3])

    with col_score:
        st.markdown(
            render_score_gauge(report["overallScore"], report["scoreBand"]),
            unsafe_allow_html=True,
        )

    with col_summary:
        st.markdown("**Executive Summary**")
        st.markdown(report.get("summary", ""))

    st.write("")

    # Tabs for all sections
    tab_sections, tab_recs, tab_copy, tab_exp, tab_signals = st.tabs([
        "📊 Section Scores",
        "🔥 Recommendations",
        "✍️ Copy Lab",
        "🧪 Experiments",
        "🔍 Raw Signals",
    ])

    # ── Tab 1: Section Scores ─────────────────────────────────────────────────
    with tab_sections:
        for section in report.get("sectionScores", []):
            st.markdown(
                render_section_bar(
                    section["name"],
                    section["score"],
                    section["maxScore"],
                    section["label"],
                    section.get("findings", []),
                ),
                unsafe_allow_html=True,
            )

    # ── Tab 2: Recommendations ────────────────────────────────────────────────
    with tab_recs:
        recs = report.get("topRecommendations", [])
        if not recs:
            st.info("No recommendations returned.")
        for i, rec in enumerate(recs):
            priority = rec.get("priority", "low")
            conf = rec.get("confidence", "medium")
            badge_class = f"badge-{priority}"
            conf_class = f"conf-{conf}"

            label = f"""<span class="badge {badge_class}">{priority.upper()}</span>
<span class="badge {conf_class}">{conf} confidence</span>"""

            with st.expander(
                f"{rec.get('issue', 'Recommendation')}",
                expanded=(i == 0),
            ):
                st.markdown(label, unsafe_allow_html=True)
                st.markdown(f"**Category:** {rec.get('category', '')}")
                st.markdown("**Suggested Fix**")
                st.markdown(rec.get("suggestion", ""))
                st.markdown("**Evidence**")
                st.markdown(
                    f'<div class="evidence-box">"{rec.get("evidence", "")}"</div>',
                    unsafe_allow_html=True,
                )
                if rec.get("hypothesis"):
                    st.markdown("**Test Hypothesis**")
                    st.markdown(f"*{rec['hypothesis']}*")
                if rec.get("expectedImpact"):
                    st.success(f"Expected impact: {rec['expectedImpact']}")

    # ── Tab 3: Copy Lab ───────────────────────────────────────────────────────
    with tab_copy:
        rewrites = report.get("copyRewrites", [])
        if not rewrites:
            st.info("No copy rewrites returned.")
        for rw in rewrites:
            rw_type = rw.get("type", "")
            tag_class = {
                "headline": "tag-headline",
                "subheadline": "tag-subheadline",
                "cta": "tag-cta",
                "value-proposition": "tag-value-proposition",
            }.get(rw_type, "tag-cta")

            type_label = rw_type.replace("-", " ").title()
            st.markdown(
                f'<span class="badge {tag_class}">{type_label}</span>',
                unsafe_allow_html=True,
            )

            col_orig, col_rw = st.columns(2)
            with col_orig:
                st.markdown("**Original**")
                st.markdown(
                    f'<div class="copy-original">{rw.get("original") or "(not detected)"}</div>',
                    unsafe_allow_html=True,
                )
            with col_rw:
                st.markdown("**Rewritten**")
                st.markdown(
                    f'<div class="copy-rewritten">{rw.get("rewritten", "")}</div>',
                    unsafe_allow_html=True,
                )
                if st.button("📋 Copy", key=f"copy_{rw_type}_{rewrites.index(rw)}"):
                    st.toast(f"Copied: {rw.get('rewritten', '')[:60]}…")

            st.caption(f"ℹ️ {rw.get('rationale', '')}")
            st.write("")

    # ── Tab 4: Experiments ────────────────────────────────────────────────────
    with tab_exp:
        experiments = report.get("experimentIdeas", [])
        if not experiments:
            st.info("No experiment ideas returned.")
        for exp in experiments:
            impact = exp.get("impactLevel", "medium")
            effort = exp.get("effortLevel", "medium")
            quad_label, quad_class = get_quad(impact, effort)

            with st.expander(exp.get("name", "Experiment")):
                st.markdown(
                    f'<span class="{quad_class}">{quad_label}</span> &nbsp;'
                    f'<span class="badge effort-{effort}">Effort: {effort}</span>'
                    f'<span class="badge impact-{impact}">Impact: {impact}</span>',
                    unsafe_allow_html=True,
                )
                st.write("")
                st.markdown("**Hypothesis**")
                st.markdown(f"*{exp.get('hypothesis', '')}*")
                st.markdown("**Variant**")
                st.markdown(exp.get("variant", ""))
                st.markdown(f"**Primary metric:** {exp.get('primaryMetric', '')}")
                guardrails = exp.get("guardrailMetrics", [])
                if guardrails:
                    st.markdown(f"**Guardrails:** {', '.join(guardrails)}")

    # ── Tab 5: Raw Signals ────────────────────────────────────────────────────
    with tab_signals:
        st.markdown("**Page Structure**")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f"**Title:** {signals['page_title'] or '*(none)*'}")
            st.markdown(f"**H1:** {signals['h1'] or '*(none — critical)*'}")
        with col_p2:
            st.markdown(f"**Nav links:** {signals['nav_links']}")
            st.markdown(f"**Outbound links:** {signals['outbound_links']}")

        if signals["h2s"]:
            st.markdown("**H2s:**")
            for h in signals["h2s"][:6]:
                st.markdown(f"- {h}")

        st.write("")
        st.markdown("**CTAs detected**")
        if signals["cta_buttons"]:
            for cta in signals["cta_buttons"]:
                st.markdown(f'- `"{cta["text"]}"` [{cta["type"]}]')
        else:
            st.warning("No CTAs detected")

        st.write("")
        st.markdown("**Form fields**")
        ff = signals["form_fields"]
        if ff:
            req = sum(1 for f in ff if f["required"])
            st.markdown(f"{len(ff)} total · {req} required")
            for f in ff:
                label = f["label"] or f["name"] or f["type"]
                st.markdown(f'- `{label}` {"*(required)*" if f["required"] else ""}')
        else:
            st.markdown("No form detected")

        st.write("")
        st.markdown("**Trust signals**")
        ts = signals["trust_signals"]
        trust_checks = [
            ("Testimonials", ts["has_testimonials"]),
            ("Star Ratings", ts["has_star_ratings"]),
            ("Logo Strip", ts["has_logo_strip"]),
            ("Money-back Guarantee", ts["has_money_back_guarantee"]),
            ("Social Proof Numbers", ts["has_social_proof"]),
            ("Security Badges", ts["has_security_badges"]),
        ]
        badges_html = " ".join(
            f'<span class="{"sig-ok" if ok else "sig-bad"}">{"✓" if ok else "✗"} {label}</span>'
            for label, ok in trust_checks
        )
        st.markdown(badges_html, unsafe_allow_html=True)

        st.write("")
        st.markdown("**Specificity signals**")
        sp = signals["specificity_signals"]
        spec_checks = [
            ("Numbers", sp["has_numbers"]),
            ("Percentages", sp["has_percentages"]),
            ("Timeframes", sp["has_timeframes"]),
            ("Guarantees", sp["has_guarantees"]),
        ]
        spec_html = " ".join(
            f'<span class="{"sig-ok" if ok else "sig-bad"}">{"✓" if ok else "✗"} {label}</span>'
            for label, ok in spec_checks
        )
        st.markdown(spec_html, unsafe_allow_html=True)
        if sp["examples"]:
            st.caption(f"Examples: {', '.join(sp['examples'])}")

        st.write("")
        rl = signals["reading_level"]
        st.markdown(
            f"**Reading level:** Est. grade {rl['estimated_grade']} · "
            f"Avg {rl['avg_sentence_length']} words/sentence · "
            f"{rl['avg_word_length']} chars/word"
        )

    st.divider()

    col_new, col_print = st.columns([2, 1])
    with col_new:
        if st.button("+ New audit", key="reset_btn"):
            st.session_state.report = None
            st.session_state.error = None
            st.rerun()
    with col_print:
        st.markdown(
            "<p style='text-align:right;color:#94a3b8;font-size:12px;padding-top:8px;'>"
            "Use Ctrl+P / Cmd+P to export as PDF</p>",
            unsafe_allow_html=True,
        )
