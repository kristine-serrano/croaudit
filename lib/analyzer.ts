import Anthropic from "@anthropic-ai/sdk";
import type {
  ExtractedSignals,
  AuditContext,
  AuditReport,
  ScoreBand,
} from "./types";

const client = new Anthropic();

type AnalysisResult = Omit<AuditReport, "signals" | "context" | "createdAt">;

export async function analyzeWithClaude(
  signals: ExtractedSignals,
  context: AuditContext
): Promise<AnalysisResult> {
  const systemPrompt = buildSystemPrompt(context);
  const userPrompt = buildUserPrompt(signals, context);

  const response = await client.messages.create({
    model: "claude-opus-4-5",
    max_tokens: 4096,
    system: systemPrompt,
    messages: [{ role: "user", content: userPrompt }],
  });

  const text =
    response.content[0].type === "text" ? response.content[0].text : "";

  return parseAnalysis(text);
}

function buildSystemPrompt(context: AuditContext): string {
  const tw = getTrafficWeighting(context.trafficSource);
  const ic = getIntentContext(context.audienceIntent);

  return `You are a world-class CRO (Conversion Rate Optimization) expert with 15+ years of experience converting landing page audits into measurable revenue gains. You specialize in ${context.trafficSource} traffic with ${context.audienceIntent}-intent audiences.

Your audits are evidence-based, specific, and prioritized by potential conversion impact. You never give generic advice — every recommendation cites the exact element it references.

SCORING RUBRIC (total 100 points):

1. Message Match & Clarity (0–20 pts)${tw.messagingWeight > 1 ? " ⭐ WEIGHTED for this traffic source" : ""}
   - H1 clarity and promise alignment with traffic source
   - Value proposition specificity (outcomes vs. features)
   - Above-fold benefit statement
   - Headline reading level appropriate for audience

2. CTA Effectiveness (0–20 pts)${tw.ctaWeight > 1 ? " ⭐ WEIGHTED for this traffic source" : ""}
   - Primary CTA uses action-oriented, specific language
   - Single dominant CTA (not competing actions)
   - CTA friction level (what happens after click is clear)
   - CTA placement and visibility

3. Trust & Credibility (0–20 pts)${tw.trustWeight > 1 ? " ⭐ WEIGHTED for this traffic source" : ""}
   - Social proof (testimonials, case studies, reviews)
   - Specificity of social proof (numbers, outcomes, names)
   - Authority signals (logos, certifications, press)
   - Risk reversal (guarantees, free trials, no-commitment)
   ${ic.trustNote}

4. Friction Reduction (0–20 pts)${tw.frictionWeight > 1 ? " ⭐ WEIGHTED for this traffic source" : ""}
   - Form field count vs. conversion goal
   - Navigation links that create exit paths
   - Competing CTAs or distracting elements
   - Clarity of next step / commitment level

5. Visual Hierarchy & Copy Quality (0–20 pts)
   - Logical narrative: Problem → Solution → Proof → CTA
   - Scannability (subheads, bullets, white space)
   - Reading level appropriate for ${context.audienceIntent}-intent audience
   - Specificity signals (numbers, %, timeframes)

TRAFFIC SOURCE: ${context.trafficSource}
${tw.notes}

AUDIENCE INTENT: ${context.audienceIntent}
${ic.notes}

CONVERSION GOAL: ${context.conversionGoal}

OUTPUT: Respond ONLY with a valid JSON object. No markdown, no explanation outside the JSON.

{
  "overallScore": <integer 0-100>,
  "scoreBand": <"Needs Major Work"|"Needs Improvement"|"Good"|"Strong"|"Excellent">,
  "summary": "<2-3 sentence executive summary with the most critical insight>",
  "sectionScores": [
    {
      "name": "<section name exactly matching rubric>",
      "score": <integer 0-20>,
      "maxScore": 20,
      "label": <"Poor"|"Below Average"|"Average"|"Good"|"Excellent">,
      "findings": ["<specific finding citing page evidence>", "<second finding>"]
    }
  ],
  "topRecommendations": [
    {
      "priority": <"critical"|"high"|"medium"|"low">,
      "category": "<e.g. Trust, CTA, Form Friction, Messaging>",
      "issue": "<what is wrong or missing>",
      "suggestion": "<specific, actionable fix with example copy if relevant>",
      "evidence": "<exact quote or data point from the page>",
      "confidence": <"high"|"medium"|"low">,
      "hypothesis": "<If [change], then [metric] will [direction] because [reason]>",
      "expectedImpact": "<e.g. +10-20% form submissions>"
    }
  ],
  "copyRewrites": [
    {
      "type": <"headline"|"subheadline"|"cta"|"value-proposition">,
      "original": "<exact original text>",
      "rewritten": "<improved version>",
      "rationale": "<1-2 sentences on why this converts better>"
    }
  ],
  "experimentIdeas": [
    {
      "name": "<concise test name>",
      "hypothesis": "<If [change] then [primary metric] will [direction] because [reasoning]>",
      "variant": "<what the variant changes vs. control>",
      "primaryMetric": "<e.g. form submission rate, CTA click rate>",
      "guardrailMetrics": ["<e.g. bounce rate>", "<e.g. session duration>"],
      "effortLevel": <"low"|"medium"|"high">,
      "impactLevel": <"low"|"medium"|"high">
    }
  ]
}`;
}

function buildUserPrompt(
  signals: ExtractedSignals,
  context: AuditContext
): string {
  const formSummary =
    signals.formFields.length > 0
      ? `${signals.formFields.length} fields total (${signals.formFields.filter((f) => f.required).length} required): ${signals.formFields
          .map((f) => `${f.label || f.name || f.type}${f.required ? "*" : ""}`)
          .join(", ")}`
      : "No forms detected";

  const ctaSummary =
    signals.ctaButtons.length > 0
      ? signals.ctaButtons.map((c) => `"${c.text}" [${c.type}]`).join(", ")
      : "None detected";

  const trustSummary = [
    signals.trustSignals.hasTestimonials
      ? `Testimonials: Yes (${signals.trustSignals.testimonialCount} detected)`
      : "Testimonials: None",
    `Star ratings: ${signals.trustSignals.hasStarRatings ? "Yes" : "No"}`,
    `Logo/client strip: ${signals.trustSignals.hasLogoStrip ? "Yes" : "No"}`,
    `Money-back guarantee: ${signals.trustSignals.hasMoneyBackGuarantee ? "Yes" : "No"}`,
    `Social proof numbers: ${signals.trustSignals.hasSocialProof ? "Yes" : "No"}`,
    `Security badges: ${signals.trustSignals.hasSecurityBadges ? "Yes" : "No"}`,
    signals.trustSignals.keywords.length > 0
      ? `Keywords found: ${signals.trustSignals.keywords.slice(0, 5).join(", ")}`
      : "No trust keywords",
  ].join(" | ");

  const specificitySummary = [
    `Numbers: ${signals.specificitySignals.hasNumbers ? "Yes" : "No"}`,
    `Percentages: ${signals.specificitySignals.hasPercentages ? "Yes" : "No"}`,
    `Timeframes: ${signals.specificitySignals.hasTimeframes ? "Yes" : "No"}`,
    `Guarantees: ${signals.specificitySignals.hasGuarantees ? "Yes" : "No"}`,
    signals.specificitySignals.examples.length > 0
      ? `Examples: ${signals.specificitySignals.examples.join(", ")}`
      : "",
  ]
    .filter(Boolean)
    .join(" | ");

  return `Audit this landing page:

CONTEXT:
- Conversion Goal: ${context.conversionGoal}
- Traffic Source: ${context.trafficSource}
- Audience Intent: ${context.audienceIntent}
- URL: ${signals.url || "Not provided (HTML paste)"}

EXTRACTED SIGNALS:

Page Title: ${signals.pageTitle || "(none)"}
H1: ${signals.h1 || "(none detected)"}
H2s (first 5): ${signals.h2s.length > 0 ? signals.h2s.slice(0, 5).join(" | ") : "(none)"}

CTAs (${signals.ctaButtons.length} found): ${ctaSummary}

Form: ${formSummary}

Navigation links in header/nav: ${signals.navLinks}
Outbound links: ${signals.outboundLinks}

Trust signals: ${trustSummary}

Specificity signals: ${specificitySummary}

Reading level: avg sentence length ${signals.readingLevel.avgSentenceLength} words, estimated grade ${signals.readingLevel.estimatedGrade}

Page text (truncated to 2000 chars):
${signals.bodyText.substring(0, 2000)}

Provide a thorough CRO audit. Cite specific evidence for every recommendation. Generate 5-7 prioritized recommendations, 2-4 copy rewrites, and 2-3 experiment ideas. Output valid JSON only.`;
}

function getTrafficWeighting(source: string) {
  const weights: Record<
    string,
    {
      messagingWeight: number;
      ctaWeight: number;
      trustWeight: number;
      frictionWeight: number;
      notes: string;
    }
  > = {
    "paid-search": {
      messagingWeight: 1.3,
      ctaWeight: 1.1,
      trustWeight: 0.9,
      frictionWeight: 1.0,
      notes:
        "Paid search users come with specific intent matching a keyword/ad. Message match between the ad and H1 is the single biggest conversion lever. Clarity beats cleverness. Remove anything that doesn't support the one conversion action.",
    },
    "paid-social": {
      messagingWeight: 1.0,
      ctaWeight: 1.0,
      trustWeight: 1.3,
      frictionWeight: 1.0,
      notes:
        "Social traffic was interrupted while scrolling — they have no prior intent. Trust-building and emotional resonance are critical. Pattern-interrupt headline, strong social proof above fold, low-friction first step.",
    },
    email: {
      messagingWeight: 1.1,
      ctaWeight: 1.2,
      trustWeight: 0.9,
      frictionWeight: 1.3,
      notes:
        "Email subscribers already trust the sender. The CTA needs to be the star — make it obvious, specific, and frictionless. Reduce form fields to the minimum needed.",
    },
    organic: {
      messagingWeight: 1.0,
      ctaWeight: 1.0,
      trustWeight: 1.0,
      frictionWeight: 1.0,
      notes:
        "Organic visitors have moderate intent and are in research mode. Balance trust-building with clear differentiation. Address objections proactively.",
    },
    referral: {
      messagingWeight: 1.1,
      ctaWeight: 1.0,
      trustWeight: 1.2,
      frictionWeight: 1.0,
      notes:
        "Referral visitors arrive with a warm recommendation. Reinforce the referring context if possible. Trust signals validate the referral. Message should match what drove the click.",
    },
  };

  return weights[source] || weights["organic"];
}

function getIntentContext(intent: string) {
  const contexts: Record<
    string,
    { trustNote: string; notes: string }
  > = {
    cold: {
      trustNote:
        "Cold audiences require heavy trust-building — they need convincing before they will share info or pay.",
      notes:
        "Cold audience: Lead with problem recognition, not solution. Use multiple social proof elements above fold. Low-commitment CTA ('See how it works' vs. 'Buy now'). Address the 'why you' question explicitly.",
    },
    warm: {
      trustNote:
        "Warm audiences know solutions exist — differentiate and reduce doubt.",
      notes:
        "Warm audience: They're solution-aware and comparing options. Lead with your differentiation. Use specific outcomes in social proof. Address the top objection (usually price or commitment) proactively.",
    },
    hot: {
      trustNote:
        "Hot audiences are ready to convert — remove friction, don't add objections.",
      notes:
        "Hot audience: They're ready. Your job is to not lose them. Minimize form fields. Make the CTA unmissable. Add a guarantee to remove last-minute doubt. Avoid navigation distractions.",
    },
  };

  return contexts[intent] || contexts["cold"];
}

function parseAnalysis(text: string): AnalysisResult {
  // Strip markdown code fences if present
  const cleaned = text
    .replace(/```json\n?/gi, "")
    .replace(/```\n?/g, "")
    .trim();

  // Extract the first JSON object
  const jsonMatch = cleaned.match(/\{[\s\S]*\}/);
  if (!jsonMatch) {
    throw new Error(
      "Claude returned an invalid response — could not find JSON object."
    );
  }

  try {
    const parsed = JSON.parse(jsonMatch[0]);

    // Validate and normalize score band
    const validBands: ScoreBand[] = [
      "Needs Major Work",
      "Needs Improvement",
      "Good",
      "Strong",
      "Excellent",
    ];
    if (!validBands.includes(parsed.scoreBand)) {
      parsed.scoreBand = scoreToband(parsed.overallScore);
    }

    return parsed as AnalysisResult;
  } catch {
    throw new Error("Claude returned malformed JSON — please retry the audit.");
  }
}

function scoreToband(score: number): ScoreBand {
  if (score < 40) return "Needs Major Work";
  if (score < 55) return "Needs Improvement";
  if (score < 70) return "Good";
  if (score < 85) return "Strong";
  return "Excellent";
}
