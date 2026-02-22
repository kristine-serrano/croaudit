"use client";

import { useState } from "react";
import type { ExtractedSignals } from "@/lib/types";

interface Props {
  signals: ExtractedSignals;
}

function Badge({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full font-medium ${
        ok
          ? "bg-green-100 text-green-700"
          : "bg-red-100 text-red-700"
      }`}
    >
      {ok ? "✓" : "✗"} {label}
    </span>
  );
}

export default function SignalsPanel({ signals }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <div className="border border-slate-200 rounded-xl overflow-hidden">
      <button
        type="button"
        className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-slate-50 transition-colors"
        onClick={() => setOpen(!open)}
      >
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-slate-700">
            Raw signals detected
          </span>
          <span className="text-xs text-slate-400">(click to expand)</span>
        </div>
        <svg
          className={`w-4 h-4 text-slate-400 transition-transform ${open ? "rotate-180" : ""}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="px-4 pb-4 border-t border-slate-100 space-y-4">
          {/* Page structure */}
          <div className="pt-3">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
              Page Structure
            </p>
            <div className="space-y-1.5">
              <div className="text-xs">
                <span className="font-medium text-slate-500">H1:</span>{" "}
                <span className="text-slate-700">
                  {signals.h1 || <em className="text-red-500">Missing</em>}
                </span>
              </div>
              {signals.h2s.length > 0 && (
                <div className="text-xs">
                  <span className="font-medium text-slate-500">H2s:</span>{" "}
                  <span className="text-slate-600">{signals.h2s.join(" · ")}</span>
                </div>
              )}
              <div className="text-xs flex gap-3">
                <span>
                  <span className="font-medium text-slate-500">Nav links:</span>{" "}
                  <span className={signals.navLinks > 5 ? "text-red-600 font-semibold" : "text-slate-700"}>
                    {signals.navLinks}
                  </span>
                </span>
                <span>
                  <span className="font-medium text-slate-500">Outbound links:</span>{" "}
                  <span className="text-slate-700">{signals.outboundLinks}</span>
                </span>
              </div>
            </div>
          </div>

          {/* CTAs */}
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
              CTAs ({signals.ctaButtons.length})
            </p>
            {signals.ctaButtons.length === 0 ? (
              <p className="text-xs text-red-500">No CTAs detected</p>
            ) : (
              <div className="flex flex-wrap gap-1.5">
                {signals.ctaButtons.map((cta, i) => (
                  <span
                    key={i}
                    className="text-xs bg-indigo-50 text-indigo-700 border border-indigo-100 px-2 py-0.5 rounded-full"
                  >
                    &ldquo;{cta.text}&rdquo; [{cta.type}]
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Form */}
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
              Form ({signals.formFields.length} fields)
            </p>
            {signals.formFields.length === 0 ? (
              <p className="text-xs text-slate-500">No form detected</p>
            ) : (
              <div className="flex flex-wrap gap-1.5">
                {signals.formFields.map((field, i) => (
                  <span
                    key={i}
                    className={`text-xs px-2 py-0.5 rounded-full border ${
                      field.required
                        ? "bg-orange-50 text-orange-700 border-orange-200"
                        : "bg-slate-50 text-slate-600 border-slate-200"
                    }`}
                  >
                    {field.label || field.name || field.type}
                    {field.required ? "*" : ""}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Trust signals */}
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
              Trust Signals
            </p>
            <div className="flex flex-wrap gap-1.5">
              <Badge ok={signals.trustSignals.hasTestimonials} label="Testimonials" />
              <Badge ok={signals.trustSignals.hasStarRatings} label="Star Ratings" />
              <Badge ok={signals.trustSignals.hasLogoStrip} label="Logo Strip" />
              <Badge ok={signals.trustSignals.hasMoneyBackGuarantee} label="Guarantee" />
              <Badge ok={signals.trustSignals.hasSocialProof} label="Social Proof Numbers" />
              <Badge ok={signals.trustSignals.hasSecurityBadges} label="Security Badges" />
            </div>
          </div>

          {/* Specificity */}
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
              Specificity Signals
            </p>
            <div className="flex flex-wrap gap-1.5">
              <Badge ok={signals.specificitySignals.hasNumbers} label="Numbers" />
              <Badge ok={signals.specificitySignals.hasPercentages} label="Percentages" />
              <Badge ok={signals.specificitySignals.hasTimeframes} label="Timeframes" />
              <Badge ok={signals.specificitySignals.hasGuarantees} label="Guarantees" />
            </div>
            {signals.specificitySignals.examples.length > 0 && (
              <p className="text-xs text-slate-500 mt-1.5">
                Examples: {signals.specificitySignals.examples.join(", ")}
              </p>
            )}
          </div>

          {/* Reading level */}
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">
              Reading Level
            </p>
            <p className="text-xs text-slate-600">
              Est. grade {signals.readingLevel.estimatedGrade} · Avg{" "}
              {signals.readingLevel.avgSentenceLength} words/sentence ·{" "}
              {signals.readingLevel.avgWordLength} chars/word
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
