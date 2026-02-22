"""
Rules-based HTML signal extractor for CRO audits.
Uses BeautifulSoup to pull structured signals from any landing page HTML.
"""

import re
import math
from urllib.parse import urlparse
from typing import Optional
from bs4 import BeautifulSoup, Tag

TRUST_KEYWORDS = [
    "testimonial", "review", "rating", "guarantee", "money-back",
    "refund", "secure", "verified", "certified", "award",
    "as seen in", "featured in", "trusted by", "customers",
    "clients", "5-star", "five star", "no risk", "risk-free",
]

CTA_ACTION_WORDS = [
    "get", "start", "try", "buy", "sign up", "signup", "register",
    "book", "schedule", "download", "claim", "join", "access",
    "watch", "request", "apply", "submit", "send", "explore",
    "unlock", "activate", "subscribe", "order", "shop", "learn",
]


def extract_signals(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    # Remove non-content elements
    for tag in soup(["script", "style", "noscript", "svg", "iframe", "head"]):
        tag.decompose()

    page_title_tag = BeautifulSoup(html, "lxml").find("title")
    page_title = page_title_tag.get_text(strip=True) if page_title_tag else ""

    h1_tag = soup.find("h1")
    h1 = re.sub(r"\s+", " ", h1_tag.get_text()).strip() if h1_tag else ""

    h2s = [re.sub(r"\s+", " ", h.get_text()).strip()
           for h in soup.find_all("h2")][:8]
    h2s = [h for h in h2s if h]

    cta_buttons = _extract_ctas(soup)
    form_fields = _extract_form_fields(soup)

    # Nav links
    nav_links = len(soup.select("nav a, header a"))

    # Outbound links
    outbound_links = 0
    if url:
        try:
            host = urlparse(url).netloc
            for a in soup.find_all("a", href=True):
                href = a.get("href", "")
                if href.startswith("http") and host not in href:
                    outbound_links += 1
        except Exception:
            pass

    body = soup.find("body")
    body_text_raw = body.get_text(separator=" ") if body else soup.get_text(separator=" ")
    body_text = re.sub(r"\s+", " ", body_text_raw).strip()

    trust_signals = _extract_trust_signals(soup, body_text.lower())
    specificity_signals = _extract_specificity_signals(body_text)
    reading_level = _calculate_reading_level(body_text)

    return {
        "url": url,
        "page_title": page_title,
        "h1": h1,
        "h2s": h2s,
        "body_text": body_text[:3000],
        "cta_buttons": cta_buttons,
        "form_fields": form_fields,
        "nav_links": nav_links,
        "outbound_links": outbound_links,
        "trust_signals": trust_signals,
        "specificity_signals": specificity_signals,
        "reading_level": reading_level,
    }


def _extract_ctas(soup: BeautifulSoup) -> list:
    ctas = []
    seen = set()

    # Buttons and submit inputs
    for el in soup.find_all(["button", "input"]):
        if el.name == "input" and el.get("type") not in ("submit", "button"):
            continue
        text = el.get_text(strip=True) or el.get("value", "")
        text = re.sub(r"\s+", " ", text).strip()
        if text and text.lower() not in seen and len(text) < 80:
            seen.add(text.lower())
            ctas.append({"text": text, "type": "button"})

    # Action-word anchor links
    for a in soup.find_all("a", href=True):
        text = re.sub(r"\s+", " ", a.get_text()).strip()
        lower = text.lower()
        href = a.get("href", "")

        if not text or len(text) > 60 or href in ("#", "/", ""):
            continue
        if any(lower.startswith(w) or f" {w} " in lower for w in CTA_ACTION_WORDS):
            if lower not in seen:
                seen.add(lower)
                ctas.append({"text": text, "type": "link", "href": href})

    return ctas[:10]


def _extract_form_fields(soup: BeautifulSoup) -> list:
    fields = []
    excluded_types = {"hidden", "submit", "button", "image", "reset"}
    for el in soup.find_all(["input", "select", "textarea"]):
        field_type = el.get("type", el.name or "input")
        if field_type in excluded_types:
            continue

        name = el.get("name", "") or el.get("id", "")
        required = el.has_attr("required") or el.get("aria-required") == "true"

        # Try to find a label
        el_id = el.get("id")
        label = ""
        if el_id:
            lbl = soup.find("label", attrs={"for": el_id})
            if lbl:
                label = lbl.get_text(strip=True)
        if not label:
            parent_label = el.find_parent("label")
            if parent_label:
                label = parent_label.get_text(strip=True)

        fields.append({
            "type": field_type,
            "label": label,
            "name": name,
            "required": required,
        })

    return fields


def _extract_trust_signals(soup: BeautifulSoup, text_lower: str) -> dict:
    found_keywords = [kw for kw in TRUST_KEYWORDS if kw in text_lower]

    has_testimonials = (
        "testimonial" in text_lower
        or bool(soup.find("blockquote"))
        or bool(soup.select('[class*="testimonial"], [class*="review"], [class*="quote"]'))
    )
    testimonial_count = max(
        len(soup.find_all("blockquote")),
        len(soup.select('[class*="testimonial"], [class*="review"]')),
    )
    has_star_ratings = (
        "★" in text_lower or "⭐" in text_lower
        or " star" in text_lower or "rating" in text_lower
        or bool(soup.select('[class*="star"], [class*="rating"]'))
    )
    has_logo_strip = (
        bool(soup.select('[class*="logo"], [class*="client"], [class*="partner"], [class*="brand"]'))
        and (len(soup.find_all("img")) > 3 or "trusted by" in text_lower or "as seen in" in text_lower)
    )
    has_money_back = (
        "money-back" in text_lower
        or "money back" in text_lower
        or ("guarantee" in text_lower and "refund" in text_lower)
    )
    has_social_proof = (
        bool(re.search(r'\d[\d,]*\s*(customer|user|client|member|company|business)s?', text_lower))
        or "joined" in text_lower
        or "trusted by" in text_lower
    )
    has_security_badges = (
        "secure" in text_lower or "ssl" in text_lower
        or "encrypted" in text_lower or "256-bit" in text_lower
        or bool(soup.select('[class*="badge"], [class*="security"], [class*="trust"], [class*="safe"]'))
    )

    return {
        "has_testimonials": has_testimonials,
        "testimonial_count": testimonial_count,
        "has_star_ratings": has_star_ratings,
        "has_logo_strip": has_logo_strip,
        "has_money_back_guarantee": has_money_back,
        "has_social_proof": has_social_proof,
        "has_security_badges": has_security_badges,
        "keywords": found_keywords,
    }


def _extract_specificity_signals(text: str) -> dict:
    pct_matches = re.findall(r'\d+(?:\.\d+)?%', text)
    num_matches = re.findall(r'\b\d[\d,]*(?:\.\d+)?\s*(?:million|billion|thousand|k|M)?\b', text)
    time_matches = re.findall(
        r'\b(?:\d+\s*(?:day|week|month|year|hour|minute)s?|in \d+|within \d+|instant|immediately)\b',
        text, re.IGNORECASE
    )
    guarantee_matches = re.findall(
        r'(?:guarantee|guaranteed|promise|no risk|risk.free)', text, re.IGNORECASE
    )

    examples = (pct_matches[:2] + time_matches[:2])[:4]

    return {
        "has_numbers": len(num_matches) > 3,
        "has_percentages": len(pct_matches) > 0,
        "has_timeframes": len(time_matches) > 0,
        "has_guarantees": len(guarantee_matches) > 0,
        "examples": examples,
    }


def _calculate_reading_level(text: str) -> dict:
    words = [w for w in text.split() if re.search(r'[a-z]', w, re.IGNORECASE)]
    sentences = [s for s in re.split(r'[.!?]+', text) if len(s.strip()) > 10]

    if not words or not sentences:
        return {"avg_word_length": 0, "avg_sentence_length": 0, "estimated_grade": 0}

    avg_word_len = sum(len(re.sub(r'[^a-z]', '', w, flags=re.IGNORECASE)) for w in words) / len(words)
    avg_sent_len = len(words) / len(sentences)
    grade = max(1, round(0.39 * avg_sent_len + 11.8 * avg_word_len - 15.59))

    return {
        "avg_word_length": round(avg_word_len, 1),
        "avg_sentence_length": round(avg_sent_len, 1),
        "estimated_grade": grade,
    }
