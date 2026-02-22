"use client";

import type { ScoreBand } from "@/lib/types";

interface Props {
  score: number;
  scoreBand: ScoreBand;
}

function getScoreColor(score: number) {
  if (score < 40) return { text: "text-red-600", bg: "bg-red-100", ring: "border-red-200", fill: "#dc2626" };
  if (score < 55) return { text: "text-orange-600", bg: "bg-orange-100", ring: "border-orange-200", fill: "#ea580c" };
  if (score < 70) return { text: "text-amber-600", bg: "bg-amber-100", ring: "border-amber-200", fill: "#d97706" };
  if (score < 85) return { text: "text-green-600", bg: "bg-green-100", ring: "border-green-200", fill: "#16a34a" };
  return { text: "text-emerald-600", bg: "bg-emerald-100", ring: "border-emerald-200", fill: "#059669" };
}

export default function ScoreGauge({ score, scoreBand }: Props) {
  const colors = getScoreColor(score);
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-3">
      {/* SVG Gauge */}
      <div className="relative w-40 h-40">
        <svg viewBox="0 0 140 140" className="w-full h-full -rotate-90">
          {/* Background track */}
          <circle
            cx="70"
            cy="70"
            r={radius}
            fill="none"
            stroke="#e2e8f0"
            strokeWidth="12"
          />
          {/* Score arc */}
          <circle
            cx="70"
            cy="70"
            r={radius}
            fill="none"
            stroke={colors.fill}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        {/* Score number */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-4xl font-bold ${colors.text}`}>{score}</span>
          <span className="text-xs text-slate-400 font-medium">/100</span>
        </div>
      </div>

      {/* Score band label */}
      <div className={`px-4 py-1.5 rounded-full border text-sm font-semibold ${colors.bg} ${colors.text} ${colors.ring}`}>
        {scoreBand}
      </div>
    </div>
  );
}
