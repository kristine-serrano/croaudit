import * as cheerio from "cheerio";
import type {
  ExtractedSignals,
  CTAButton,
  FormField,
  TrustSignals,
  SpecificitySignals,
  ReadingLevel,
} from "./types";

const TRUST_KEYWORDS = [
  "testimonial",
  "review",
  "rating",
  "guarantee",
  "money-back",
  "refund",
  "secure",
  "verified",
  "certified",
  "award",
  "as seen in",
  "featured in",
  "trusted by",
  "customers",
  "clients",
  "5-star",
  "five star",
  "no risk",
  "risk-free",
];

const CTA_ACTION_WORDS = [
  "get",
  "start",
  "try",
  "buy",
  "sign up",
  "signup",
  "register",
  "book",
  "schedule",
  "download",
  "claim",
  "join",
  "access",
  "watch",
  "request",
  "apply",
  "submit",
  "send",
  "explore",
  "unlock",
  "activate",
  "subscribe",
  "order",
];

export function extractSignals(html: string, url: string): ExtractedSignals {
  const $ = cheerio.load(html);

  // Remove scripts, styles, and other non-content elements
  $("script, style, noscript, svg, iframe").remove();

  const pageTitle = $("title").text().trim();
  const h1 = $("h1").first().text().replace(/\s+/g, " ").trim();
  const h2s = $("h2")
    .map((_, el) => $(el).text().replace(/\s+/g, " ").trim())
    .get()
    .filter(Boolean)
    .slice(0, 8);

  // Extract CTAs
  const ctaButtons = extractCTAs($);

  // Extract form fields
  const formFields = extractFormFields($);

  // Count nav links (in header/nav elements)
  const navLinks = $("nav a, header a").length;

  // Count outbound links
  let outboundLinks = 0;
  try {
    if (url) {
      const urlHost = new URL(url).hostname;
      $("a[href]").each((_, el) => {
        const href = $(el).attr("href") || "";
        if (href.startsWith("http") && !href.includes(urlHost)) {
          outboundLinks++;
        }
      });
    }
  } catch {
    // Invalid URL, skip outbound count
  }

  // Extract trust signals
  const trustSignals = extractTrustSignals($);

  // Extract body text (cleaned)
  const bodyText = $("body")
    .text()
    .replace(/\s+/g, " ")
    .replace(/[^\w\s.,!?%$-]/g, " ")
    .trim();

  // Extract specificity signals from body text
  const specificitySignals = extractSpecificitySignals(bodyText);

  // Calculate reading level
  const readingLevel = calculateReadingLevel(bodyText);

  return {
    url,
    pageTitle,
    h1,
    h2s,
    bodyText: bodyText.substring(0, 3000),
    ctaButtons,
    formFields,
    navLinks,
    outboundLinks,
    trustSignals,
    specificitySignals,
    readingLevel,
  };
}

function extractCTAs($: cheerio.CheerioAPI): CTAButton[] {
  const ctas: CTAButton[] = [];
  const seen = new Set<string>();

  // Buttons and submit inputs
  $('button, input[type="submit"], input[type="button"]').each((_, el) => {
    const text =
      $(el).text().replace(/\s+/g, " ").trim() || $(el).attr("value") || "";
    if (text && !seen.has(text.toLowerCase())) {
      seen.add(text.toLowerCase());
      ctas.push({ text, type: "button" });
    }
  });

  // Links that look like CTAs (short text with action words)
  $("a").each((_, el) => {
    const text = $(el).text().replace(/\s+/g, " ").trim();
    const lowerText = text.toLowerCase();
    const href = $(el).attr("href") || "";

    // Skip empty, navigation, or very long link text
    if (!text || text.length > 60 || text.length < 2) return;
    if (href === "#" || href === "/" || href === "") return;

    const isActionLink = CTA_ACTION_WORDS.some((word) =>
      lowerText.startsWith(word) || lowerText.includes(` ${word} `)
    );

    if (isActionLink && !seen.has(lowerText)) {
      seen.add(lowerText);
      ctas.push({ text, type: "link", href });
    }
  });

  return ctas.slice(0, 10);
}

function extractFormFields($: cheerio.CheerioAPI): FormField[] {
  const fields: FormField[] = [];

  $(
    'input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="image"]), select, textarea'
  ).each((_, el) => {
    const type =
      $(el).attr("type") || el.type === "tag" ? el.name : "input";
    const name = $(el).attr("name") || $(el).attr("id") || "";
    const required =
      $(el).attr("required") !== undefined || $(el).attr("aria-required") === "true";

    // Find associated label
    const id = $(el).attr("id");
    let label = id ? $(`label[for="${id}"]`).text().trim() : "";
    if (!label) {
      // Try wrapping label
      label = $(el).closest("label").text().replace($(el).text(), "").trim();
    }

    fields.push({ type: type || "input", label, required, name });
  });

  return fields;
}

function extractTrustSignals($: cheerio.CheerioAPI): TrustSignals {
  const text = $("body").text().toLowerCase();
  const keywords: string[] = [];

  TRUST_KEYWORDS.forEach((keyword) => {
    if (text.includes(keyword)) {
      keywords.push(keyword);
    }
  });

  const hasTestimonials =
    text.includes("testimonial") ||
    $("blockquote").length > 0 ||
    $('[class*="testimonial"], [class*="review"], [class*="quote"]').length > 0;

  const testimonialCount = Math.max(
    $("blockquote").length,
    $('[class*="testimonial"], [class*="review"]').length
  );

  const hasStarRatings =
    text.includes("★") ||
    text.includes("⭐") ||
    text.includes(" star") ||
    text.includes("rating") ||
    $('[class*="star"], [class*="rating"]').length > 0;

  const hasLogoStrip =
    $('[class*="logo"], [class*="client"], [class*="partner"], [class*="brand"]')
      .length > 0 &&
    ($("img").length > 3 || text.includes("trusted by") || text.includes("as seen in"));

  const hasMoneyBackGuarantee =
    text.includes("money-back") ||
    text.includes("money back") ||
    (text.includes("guarantee") && text.includes("refund"));

  const hasSocialProof =
    /\d+,?\d*\s*(customer|user|client|member|company|business|brand)s?/.test(
      text
    ) ||
    text.includes("joined") ||
    text.includes("trusted by");

  const hasSecurityBadges =
    text.includes("secure") ||
    text.includes("ssl") ||
    text.includes("encrypted") ||
    text.includes("256-bit") ||
    $('[class*="badge"], [class*="security"], [class*="trust"], [class*="safe"]')
      .length > 0;

  return {
    hasTestimonials,
    testimonialCount,
    hasStarRatings,
    hasLogoStrip,
    hasMoneyBackGuarantee,
    hasSocialProof,
    hasSecurityBadges,
    keywords,
  };
}

function extractSpecificitySignals(text: string): SpecificitySignals {
  const percentageMatches = text.match(/\d+(\.\d+)?%/g) || [];
  const numberMatches =
    text.match(/\b\d[\d,]*(\.\d+)?\s*(million|billion|thousand|k|M)?\b/g) ||
    [];
  const timeframeMatches =
    text.match(
      /\b(\d+\s*(day|week|month|year|hour|minute)s?|in \d+|within \d+|instant|immediately)\b/gi
    ) || [];
  const guaranteeMatches =
    text.match(/(guarantee|guaranteed|promise|no risk|risk.free)/gi) || [];

  const examples = [
    ...percentageMatches.slice(0, 2),
    ...timeframeMatches.slice(0, 2),
  ].filter(Boolean);

  return {
    hasNumbers: numberMatches.length > 3,
    hasPercentages: percentageMatches.length > 0,
    hasTimeframes: timeframeMatches.length > 0,
    hasGuarantees: guaranteeMatches.length > 0,
    examples,
  };
}

function calculateReadingLevel(text: string): ReadingLevel {
  const words = text
    .split(/\s+/)
    .filter((w) => w.length > 0 && /[a-z]/i.test(w));
  const sentences = text
    .split(/[.!?]+/)
    .filter((s) => s.trim().length > 10);

  if (words.length === 0 || sentences.length === 0) {
    return { avgWordLength: 0, avgSentenceLength: 0, estimatedGrade: 0 };
  }

  const avgWordLength =
    words.reduce((sum, w) => sum + w.replace(/[^a-z]/gi, "").length, 0) /
    words.length;
  const avgSentenceLength = words.length / sentences.length;

  // Flesch-Kincaid Grade Level approximation
  const estimatedGrade = Math.max(
    1,
    Math.round(0.39 * avgSentenceLength + 11.8 * avgWordLength - 15.59)
  );

  return {
    avgWordLength: Math.round(avgWordLength * 10) / 10,
    avgSentenceLength: Math.round(avgSentenceLength * 10) / 10,
    estimatedGrade,
  };
}
