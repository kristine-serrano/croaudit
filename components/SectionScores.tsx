"use client";

import { useState } from "react";
import type { SectionScore } from "@/lib/types";

interface Props {
  sections: SectionScore[];
}

function getLabelColor(label: string) {
  switch (label) {
    case "Poor": return "text-red-600 bg-red-50";
    case "Below Average": return "text-orange-600 bg-orange-50";
    case "Average": return "text-amber-600 bg-amber-50";
    case "Good": return "text-green-600 bg-green-50";
    case "Excellent": return "text-emerald-600 bg-emerald-50";
    default: return "text-slate-600 bg-slate-50";
  }
}

function getBarColor(score: number, max: number) {
  const pct = score / max;
  if (pct < 0.4) return "bg-red-500";
  if (pct < 0.55) return "bg-orange-500";
  if (pct < 0.7) return "bg-amber-500";
  if (pct < 0.85) return "bg-green-500";
  return "bg-emerald-500";
}

export default function SectionScores({ sections }: Props) {
  const [expanded, setExpanded] = useState<number | null>(null);

  return (
    <div className="space-y-3">
      {sections.map((section, i) => {
        const pct = Math.round((section.score / section.maxScore) * 100);
        const isExpanded = expanded === i;

        return (
          <div
            key={section.name}
            className="border border-slate-200 rounded-xl overflow-hidden"
          >
            <button
              type="button"
              className="w-full px-4 py-3 text-left hover:bg-slate-50 transition-colors"
              onClick={() => setExpanded(isExpanded ? null : i)}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-slate-800">
                  {section.name}
                </span>
                <div className="flex items-center gap-2">
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded-full ${getLabelColor(section.label)}`}
                  >
                    {section.label}
                  </span>
                  <span className="text-sm font-bold text-slate-700">
                    {section.score}
                    <span className="text-slate-400 font-normal">
                      /{section.maxScore}
                    </span>
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
              {/* Progress bar */}
              <div className="h-2 rounded-full bg-slate-100">
                <div
                  className={`h-2 rounded-full transition-all duration-700 ${getBarColor(section.score, section.maxScore)}`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </button>

            {/* Findings */}
            {isExpanded && section.findings.length > 0 && (
              <div className="px-4 pb-4 border-t border-slate-100 bg-slate-50">
                <ul className="mt-3 space-y-1.5">
                  {section.findings.map((finding, j) => (
                    <li key={j} className="flex items-start gap-2 text-sm text-slate-600">
                      <span className="mt-1 w-1.5 h-1.5 rounded-full bg-slate-400 shrink-0" />
                      {finding}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
