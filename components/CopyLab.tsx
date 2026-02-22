"use client";

import { useState } from "react";
import type { CopyRewrite } from "@/lib/types";

const TYPE_LABELS: Record<CopyRewrite["type"], { label: string; color: string }> = {
  headline: { label: "Headline", color: "bg-purple-100 text-purple-700" },
  subheadline: { label: "Subheadline", color: "bg-blue-100 text-blue-700" },
  cta: { label: "CTA", color: "bg-indigo-100 text-indigo-700" },
  "value-proposition": { label: "Value Prop", color: "bg-teal-100 text-teal-700" },
};

interface Props {
  rewrites: CopyRewrite[];
}

export default function CopyLab({ rewrites }: Props) {
  const [copied, setCopied] = useState<number | null>(null);

  const handleCopy = async (text: string, i: number) => {
    await navigator.clipboard.writeText(text);
    setCopied(i);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="space-y-4">
      {rewrites.map((rewrite, i) => {
        const typeConfig = TYPE_LABELS[rewrite.type] || {
          label: rewrite.type,
          color: "bg-slate-100 text-slate-600",
        };

        return (
          <div key={i} className="border border-slate-200 rounded-xl overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 bg-slate-50 border-b border-slate-100">
              <span
                className={`text-xs font-semibold px-2.5 py-1 rounded-full ${typeConfig.color}`}
              >
                {typeConfig.label}
              </span>
              <button
                type="button"
                onClick={() => handleCopy(rewrite.rewritten, i)}
                className="text-xs font-medium text-indigo-600 hover:text-indigo-800 flex items-center gap-1.5 transition-colors"
              >
                {copied === i ? (
                  <>
                    <svg className="w-4 h-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-green-600">Copied!</span>
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    Copy rewrite
                  </>
                )}
              </button>
            </div>

            <div className="p-4 space-y-3">
              {/* Before / After */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1.5">
                    Original
                  </p>
                  <div className="bg-red-50 border border-red-100 rounded-lg px-3 py-2.5">
                    <p className="text-sm text-slate-700 leading-relaxed">
                      {rewrite.original || "(not detected)"}
                    </p>
                  </div>
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1.5">
                    Rewritten
                  </p>
                  <div className="bg-green-50 border border-green-100 rounded-lg px-3 py-2.5">
                    <p className="text-sm text-slate-800 font-medium leading-relaxed">
                      {rewrite.rewritten}
                    </p>
                  </div>
                </div>
              </div>

              {/* Rationale */}
              <div className="text-xs text-slate-500 flex items-start gap-1.5">
                <svg className="w-3.5 h-3.5 mt-0.5 text-slate-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {rewrite.rationale}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
