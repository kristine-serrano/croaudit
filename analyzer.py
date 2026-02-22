"""
Claude LLM scoring layer for CRO audits.
Takes extracted HTML signals + audit context and returns structured analysis.
"""

import json
import re
import anthropic

client = anthropic.Anthropic()

TRAFFIC_WEIGHTS = {
    "paid-search": {
        "messaging": 1.3, "cta": 1.1, "trust": 0.9, "friction": 1.0,
        "notes": (
            "Paid search users come with specific intent matching a keyword/ad. "
            "Message match between the ad and H1 is the single biggest conversion lever. "
            "Clarity beats cleverness."
        ),
    },
    "paid-social": {
        "messaging": 1.0, "cta": 1.0, "trust": 1.3, "friction": 1.0,
        "notes": (
            "Social traffic was interrupted while scrolling — they have no prior intent. "
            "Trust-building and emotional resonance are critical. "
            "Pattern-interrupt headline, strong social proof above fold."
        ),
    },
    "email": {
        "messaging": 1.1, "cta": 1.2, "trust": 0.9, "friction": 1.3,
        "notes": (
            "Email subscribers already trust the sender. "
            "The CTA needs to be the star — obvious, specific, frictionless. "
            "Reduce form fields to the absolute minimum."
        ),
    },
    "organic": {
        "messaging": 1.0, "cta": 1.0, "trust": 1.0, "friction": 1.0,
        "notes": (
            "Organic visitors have moderate intent and are in research mode. "
            "Balance trust-building with clear differentiation."
        ),
    },
    "referral": {
        "messaging": 1.1, "cta": 1.0, "trust": 1.2, "friction": 1.0,
        "notes": (
            "Referral visitors arrive with a warm recommendation. "
            "Trust signals validate the referral. "
            "Message should match what drove the click."
        ),
    },
}

INTENT_CONTEXT = {
    "cold": {
        "trust_note": "Cold audiences require heavy trust-building before sharing info.",
        "notes": (
            "Lead with problem recognition, not solution. "
            "Multiple social proof elements above fold. "
            "Low-commitment CTA ('See how it works' not 'Buy now')."
        ),
    },
    "warm": {
        "trust_note": "Warm audiences know solutions exist — differentiate and reduce doubt.",
        "notes": (
            "They're comparing options. Lead with differentiation. "
            "Use specific outcomes in social proof. "
            "Address the top objection (usually price or commitment) proactively."
        ),
    },
    "hot": {
        "trust_note": "Hot audiences are ready — remove friction, don't add objections.",
        "notes": (
            "They're ready to convert. Make the CTA unmissable. "
            "Minimize form fields. Add a guarantee to remove last-minute doubt. "
            "Avoid navigation distractions."
        ),
    },
}


def analyze_with_claude(signals: dict, context: dict) -> dict:
    tw = TRAFFIC_WEIGHTS.get(context["traffic_source"], TRAFFIC_WEIGHTS["organic"])
    ic = INTENT_CONTEXT.get(context["audience_intent"], INTENT_CONTEXT["cold"])

    system_prompt = _build_system_prompt(context, tw, ic)
    user_prompt = _build_user_prompt(signals, context)

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    text = response.content[0].text if response.content else ""
    return _parse_response(text)


def _build_system_prompt(context: dict, tw: dict, ic: dict) -> str:
    ts = context["traffic_source"]
    ai = context["audience_intent"]
    goal = context["conversion_goal"]

    def weighted(label: str, key: str) -> str:
        return f"{label} (0–20 pts){' ⭐ WEIGHTED' if tw[key] > 1 else ''}"

    return f"""You are a world-class CRO (Conversion Rate Optimization) expert with 15+ years of experience. You specialize in {ts} traffic with {ai}-intent audiences.

Your audits are evidence-based and specific. Every recommendation cites the exact element it references. Never give generic advice.

SCORING RUBRIC (total 100 points):

1. {weighted("Message Match & Clarity", "messaging")}
   - H1 clarity and promise alignment with traffic source
   - Value proposition specificity (outcomes vs features)
   - Above-fold benefit statement
   - Headline reading level appropriate for audience

2. {weighted("CTA Effectiveness", "cta")}
   - Action-oriented, specific language
   - Single dominant CTA (no competing actions)
   - Friction level (what happens after click is clear)
   - Placement and visibility

3. {weighted("Trust & Credibility", "trust")}
   - Social proof (testimonials, case studies, reviews)
   - Specificity of social proof (numbers, outcomes, names)
   - Authority signals (logos, certifications, press)
   - Risk reversal (guarantees, free trials, no-commitment)
   {ic["trust_note"]}

4. {weighted("Friction Reduction", "friction")}
   - Form field count vs conversion goal
   - Navigation links that create exit paths
   - Competing CTAs or distracting elements
   - Clarity of next step / commitment level

5. Visual Hierarchy & Copy Quality (0–20 pts)
   - Logical narrative: Problem → Solution → Proof → CTA
   - Scannability (subheads, bullets, white space)
   - Reading level appropriate for {ai}-intent audience
   - Specificity signals (numbers, %, timeframes)

TRAFFIC SOURCE: {ts}
{tw["notes"]}

AUDIENCE INTENT: {ai}
{ic["notes"]}

CONVERSION GOAL: {goal}

OUTPUT: Respond ONLY with a valid JSON object. No markdown, no text outside the JSON.

{{
  "overallScore": <integer 0-100>,
  "scoreBand": <"Needs Major Work"|"Needs Improvement"|"Good"|"Strong"|"Excellent">,
  "summary": "<2-3 sentence executive summary with most critical insight>",
  "sectionScores": [
    {{
      "name": "<section name>",
      "score": <integer 0-20>,
      "maxScore": 20,
      "label": <"Poor"|"Below Average"|"Average"|"Good"|"Excellent">,
      "findings": ["<specific finding citing page evidence>", "<second finding>"]
    }}
  ],
  "topRecommendations": [
    {{
      "priority": <"critical"|"high"|"medium"|"low">,
      "category": "<e.g. Trust, CTA, Form Friction, Messaging>",
      "issue": "<what is wrong or missing>",
      "suggestion": "<specific actionable fix with example copy if relevant>",
      "evidence": "<exact quote or data point from the page>",
      "confidence": <"high"|"medium"|"low">,
      "hypothesis": "<If [change] then [metric] will [direction] because [reason]>",
      "expectedImpact": "<e.g. +10-20% form submissions>"
    }}
  ],
  "copyRewrites": [
    {{
      "type": <"headline"|"subheadline"|"cta"|"value-proposition">,
      "original": "<exact original text>",
      "rewritten": "<improved version>",
      "rationale": "<1-2 sentences on why this converts better>"
    }}
  ],
  "experimentIdeas": [
    {{
      "name": "<concise test name>",
      "hypothesis": "<If [change] then [metric] will [direction] because [reason]>",
      "variant": "<what the variant changes vs control>",
      "primaryMetric": "<e.g. form submission rate>",
      "guardrailMetrics": ["<metric 1>", "<metric 2>"],
      "effortLevel": <"low"|"medium"|"high">,
      "impactLevel": <"low"|"medium"|"high">
    }}
  ]
}}"""


def _build_user_prompt(signals: dict, context: dict) -> str:
    ff = signals["form_fields"]
    form_summary = (
        f"{len(ff)} fields total ({sum(1 for f in ff if f['required'])} required): "
        + ", ".join(f"{f['label'] or f['name'] or f['type']}{'*' if f['required'] else ''}" for f in ff)
        if ff else "No forms detected"
    )

    ctas = signals["cta_buttons"]
    cta_summary = (
        ", ".join(f'"{c["text"]}" [{c["type"]}]' for c in ctas)
        if ctas else "None detected"
    )

    ts = signals["trust_signals"]
    trust_summary = " | ".join([
        f"Testimonials: {'Yes (' + str(ts['testimonial_count']) + ' detected)' if ts['has_testimonials'] else 'None'}",
        f"Star ratings: {'Yes' if ts['has_star_ratings'] else 'No'}",
        f"Logo strip: {'Yes' if ts['has_logo_strip'] else 'No'}",
        f"Money-back guarantee: {'Yes' if ts['has_money_back_guarantee'] else 'No'}",
        f"Social proof numbers: {'Yes' if ts['has_social_proof'] else 'No'}",
        f"Security badges: {'Yes' if ts['has_security_badges'] else 'No'}",
        f"Keywords: {', '.join(ts['keywords'][:5]) if ts['keywords'] else 'None'}",
    ])

    sp = signals["specificity_signals"]
    spec_summary = " | ".join([
        f"Numbers: {'Yes' if sp['has_numbers'] else 'No'}",
        f"Percentages: {'Yes' if sp['has_percentages'] else 'No'}",
        f"Timeframes: {'Yes' if sp['has_timeframes'] else 'No'}",
        f"Guarantees: {'Yes' if sp['has_guarantees'] else 'No'}",
        f"Examples: {', '.join(sp['examples']) if sp['examples'] else 'None'}",
    ])

    rl = signals["reading_level"]

    return f"""Audit this landing page:

CONTEXT:
- Conversion Goal: {context['conversion_goal']}
- Traffic Source: {context['traffic_source']}
- Audience Intent: {context['audience_intent']}
- URL: {signals['url'] or 'Not provided (HTML paste)'}

EXTRACTED SIGNALS:

Page Title: {signals['page_title'] or '(none)'}
H1: {signals['h1'] or '(none detected)'}
H2s (first 5): {' | '.join(signals['h2s'][:5]) or '(none)'}

CTAs ({len(ctas)} found): {cta_summary}

Form: {form_summary}

Navigation links in header/nav: {signals['nav_links']}
Outbound links: {signals['outbound_links']}

Trust signals: {trust_summary}

Specificity signals: {spec_summary}

Reading level: avg sentence length {rl['avg_sentence_length']} words, estimated grade {rl['estimated_grade']}

Page text (truncated to 2000 chars):
{signals['body_text'][:2000]}

Provide a thorough CRO audit. Cite specific evidence for every recommendation. Generate 5-7 prioritized recommendations, 2-4 copy rewrites, and 2-3 experiment ideas. Output valid JSON only."""


def _parse_response(text: str) -> dict:
    # Strip markdown fences if present
    cleaned = re.sub(r"```json\s*", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"```", "", cleaned).strip()

    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        raise ValueError("Claude returned a response without a JSON object.")

    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude returned malformed JSON: {e}") from e

    # Normalize score band
    valid_bands = {"Needs Major Work", "Needs Improvement", "Good", "Strong", "Excellent"}
    if data.get("scoreBand") not in valid_bands:
        score = data.get("overallScore", 0)
        if score < 40:
            data["scoreBand"] = "Needs Major Work"
        elif score < 55:
            data["scoreBand"] = "Needs Improvement"
        elif score < 70:
            data["scoreBand"] = "Good"
        elif score < 85:
            data["scoreBand"] = "Strong"
        else:
            data["scoreBand"] = "Excellent"

    return data
