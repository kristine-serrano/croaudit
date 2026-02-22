"use client";

import type { ExperimentIdea } from "@/lib/types";

const EFFORT_COLORS = {
  low: "bg-green-100 text-green-700",
  medium: "bg-amber-100 text-amber-700",
  high: "bg-red-100 text-red-700",
};

const IMPACT_COLORS = {
  low: "bg-slate-100 text-slate-600",
  medium: "bg-blue-100 text-blue-700",
  high: "bg-indigo-100 text-indigo-700",
};

const MATRIX_QUAD = {
  "high-low": { label: "Quick Win", color: "bg-green-600" },
  "high-medium": { label: "Quick Win", color: "bg-green-600" },
  "high-high": { label: "Major Project", color: "bg-indigo-600" },
  "medium-low": { label: "Fill-In", color: "bg-slate-400" },
  "medium-medium": { label: "Schedule", color: "bg-amber-500" },
  "medium-high": { label: "Quick Win", color: "bg-green-500" },
  "low-low": { label: "Avoid", color: "bg-red-400" },
  "low-medium": { label: "Fill-In", color: "bg-slate-400" },
  "low-high": { label: "Schedule", color: "bg-amber-500" },
};

function getQuadrant(impact: string, effort: string) {
  const key = `${impact}-${effort}` as keyof typeof MATRIX_QUAD;
  return MATRIX_QUAD[key] || { label: "Schedule", color: "bg-slate-400" };
}

interface Props {
  experiments: ExperimentIdea[];
}

export default function ExperimentBacklog({ experiments }: Props) {
  return (
    <div className="space-y-4">
      {experiments.map((exp, i) => {
        const quad = getQuadrant(exp.impactLevel, exp.effortLevel);

        return (
          <div key={i} className="border border-slate-200 rounded-xl p-4 space-y-3">
            {/* Header */}
            <div className="flex items-start justify-between gap-3">
              <div>
                <h4 className="text-sm font-bold text-slate-800">{exp.name}</h4>
                <p className="text-xs text-slate-500 mt-0.5">
                  Primary metric: {exp.primaryMetric}
                </p>
              </div>
              <span
                className={`shrink-0 text-xs font-bold text-white px-2.5 py-1 rounded-full ${quad.color}`}
              >
                {quad.label}
              </span>
            </div>

            {/* Hypothesis */}
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">
                Hypothesis
              </p>
              <p className="text-sm text-slate-600 italic">{exp.hypothesis}</p>
            </div>

            {/* Variant */}
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">
                Variant
              </p>
              <p className="text-sm text-slate-700">{exp.variant}</p>
            </div>

            {/* Guardrail metrics */}
            {exp.guardrailMetrics.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">
                  Guardrail metrics
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {exp.guardrailMetrics.map((m, j) => (
                    <span
                      key={j}
                      className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full"
                    >
                      {m}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Effort vs Impact */}
            <div className="flex items-center gap-3 pt-1 border-t border-slate-100">
              <div className="flex items-center gap-1.5">
                <span className="text-xs text-slate-400">Effort:</span>
                <span
                  className={`text-xs font-semibold px-2 py-0.5 rounded-full capitalize ${EFFORT_COLORS[exp.effortLevel]}`}
                >
                  {exp.effortLevel}
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-xs text-slate-400">Impact:</span>
                <span
                  className={`text-xs font-semibold px-2 py-0.5 rounded-full capitalize ${IMPACT_COLORS[exp.impactLevel]}`}
                >
                  {exp.impactLevel}
                </span>
              </div>
            </div>
          </div>
        );
      })}

      {/* Export hint */}
      <p className="text-xs text-slate-400 text-center">
        Use browser print (Ctrl+P / Cmd+P) to export experiments as PDF
      </p>
    </div>
  );
}
