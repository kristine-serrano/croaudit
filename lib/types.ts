export type TrafficSource =
  | "paid-search"
  | "paid-social"
  | "email"
  | "organic"
  | "referral";

export type AudienceIntent = "cold" | "warm" | "hot";

export type Priority = "critical" | "high" | "medium" | "low";

export type Confidence = "high" | "medium" | "low";

export type ScoreBand =
  | "Needs Major Work"
  | "Needs Improvement"
  | "Good"
  | "Strong"
  | "Excellent";

export interface AuditContext {
  url?: string;
  conversionGoal: string;
  trafficSource: TrafficSource;
  audienceIntent: AudienceIntent;
}

export interface CTAButton {
  text: string;
  type: "button" | "link" | "input";
  href?: string;
}

export interface FormField {
  type: string;
  label?: string;
  required: boolean;
  name?: string;
}

export interface TrustSignals {
  hasTestimonials: boolean;
  testimonialCount: number;
  hasStarRatings: boolean;
  hasLogoStrip: boolean;
  hasMoneyBackGuarantee: boolean;
  hasSocialProof: boolean;
  hasSecurityBadges: boolean;
  keywords: string[];
}

export interface SpecificitySignals {
  hasNumbers: boolean;
  hasPercentages: boolean;
  hasTimeframes: boolean;
  hasGuarantees: boolean;
  examples: string[];
}

export interface ReadingLevel {
  avgWordLength: number;
  avgSentenceLength: number;
  estimatedGrade: number;
}

export interface ExtractedSignals {
  url: string;
  pageTitle: string;
  h1: string;
  h2s: string[];
  bodyText: string;
  ctaButtons: CTAButton[];
  formFields: FormField[];
  navLinks: number;
  outboundLinks: number;
  trustSignals: TrustSignals;
  specificitySignals: SpecificitySignals;
  readingLevel: ReadingLevel;
}

export interface SectionScore {
  name: string;
  score: number;
  maxScore: number;
  label: "Poor" | "Below Average" | "Average" | "Good" | "Excellent";
  findings: string[];
}

export interface Recommendation {
  priority: Priority;
  category: string;
  issue: string;
  suggestion: string;
  evidence: string;
  confidence: Confidence;
  hypothesis?: string;
  expectedImpact?: string;
}

export interface CopyRewrite {
  type: "headline" | "subheadline" | "cta" | "value-proposition";
  original: string;
  rewritten: string;
  rationale: string;
}

export interface ExperimentIdea {
  name: string;
  hypothesis: string;
  variant: string;
  primaryMetric: string;
  guardrailMetrics: string[];
  effortLevel: "low" | "medium" | "high";
  impactLevel: "low" | "medium" | "high";
}

export interface AuditReport {
  context: AuditContext;
  signals: ExtractedSignals;
  overallScore: number;
  scoreBand: ScoreBand;
  summary: string;
  sectionScores: SectionScore[];
  topRecommendations: Recommendation[];
  copyRewrites: CopyRewrite[];
  experimentIdeas: ExperimentIdea[];
  createdAt: string;
}

export interface AuditRequest {
  url?: string;
  html?: string;
  context: AuditContext;
}

export interface AuditResponse {
  report?: AuditReport;
  error?: string;
}
