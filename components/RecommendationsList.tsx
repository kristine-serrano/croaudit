"use client";

import { useState } from "react";
import type { Recommendation } from "@/lib/types";

const PRIORITY_CONFIG = {
  critical: {
    label: "Critical",
    classes: "bg-red-100 text-red-700 border-red-200",
    dot: "bg-red-500",
    border: "border-l-red-500",
  },
  high: {
    label: "High",
    classes: "bg-orange-100 text-orange-700 border-orange-200",
    dot: "bg-orange-500",
    border: "border-l-orange-500",
  },
  medium: {
    label: "Medium",
    classes: "bg-amber-100 text-amber-700 border-amber-200",
    dot: "bg-amber-500",
    border: "border-l-amber-400",
  },
  low: {
    label: "Low",
    classes: "bg-slate-100 text-slate-600 border-slate-200",
    dot: "bg-slate-400",
    border: "border-l-slate-300",
  },
};

const CONFIDENCE_BADGE = {
  high: "bg-green-100 text-green-700",
  medium: "bg-amber-100 text-amber-700",
  low: "bg-slate-100 text-slate-600",
};

interface Props {
  recommendations: Recommendation[];
}

export default function RecommendationsList({ recommendations }: Props) {
  const [expanded, setExpanded] = useState<number | null>(0);

  return (
    <div className="space-y-3">
      {recommendations.map((rec, i) => {
        const pc = PRIORITY_CONFIG[rec.priority];
        const isExpanded = expanded === i;

        return (
          <div
            key={i}
            className={`border border-slate-200 rounded-xl border-l-4 overflow-hidden ${pc.border}`}
          >
            <button
              type="button"
              className="w-full px-4 py-4 text-left hover:bg-slate-50 transition-colors"
              onClick={() => setExpanded(isExpanded ? null : i)}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3">
                  <span className="mt-0.5 flex-shrink-0">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${pc.classes}`}
                    >
                      {pc.label}
                    </span>
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-slate-800">
                      {rec.issue}
                    </p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {rec.category}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full font-medium ${CONFIDENCE_BADGE[rec.confidence]}`}
                  >
                    {rec.confidence} confidence
                  </span>
                  <svg
                    className={`w-4 h-4 text-slate-400 transition-transform ${
                      isExpanded ? "rotate-180" : ""
                    }`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </div>
              </div>
            </button>

            {isExpanded && (
              <div className="px-4 pb-4 border-t border-slate-100 bg-slate-50 space-y-3">
                {/* Suggestion */}
                <div className="pt-3">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                    Suggested Fix
                  </p>
                  <p className="text-sm text-slate-700">{rec.suggestion}</p>
                </div>

                {/* Evidence */}
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                    Evidence
                  </p>
                  <div className="bg-white border border-slate-200 rounded-lg px-3 py-2">
                    <p className="text-sm text-slate-600 italic">
                      &ldquo;{rec.evidence}&rdquo;
                    </p>
                  </div>
                </div>

                {/* Hypothesis */}
                {rec.hypothesis && (
                  <div>
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                      Test Hypothesis
                    </p>
                    <p className="text-sm text-slate-600">{rec.hypothesis}</p>
                  </div>
                )}

                {/* Expected impact */}
                {rec.expectedImpact && (
                  <div className="inline-flex items-center gap-1.5 bg-green-50 text-green-700 text-sm px-3 py-1.5 rounded-lg border border-green-200">
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                      />
                    </svg>
                    <span className="font-semibold">Expected:</span>{" "}
                    {rec.expectedImpact}
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
