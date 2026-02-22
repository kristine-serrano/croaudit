"use client";

import { useState } from "react";
import type { AuditContext, TrafficSource, AudienceIntent } from "@/lib/types";

const CONVERSION_GOALS = [
  "Generate leads (book a call)",
  "Generate leads (get a quote)",
  "Generate leads (free trial signup)",
  "Collect emails / newsletter signup",
  "Webinar or event registration",
  "App download",
  "Ecommerce purchase",
  "Custom…",
];

const TRAFFIC_SOURCES: { value: TrafficSource; label: string; icon: string }[] =
  [
    { value: "paid-search", label: "Paid Search", icon: "🔍" },
    { value: "paid-social", label: "Paid Social", icon: "📱" },
    { value: "email", label: "Email Campaign", icon: "📧" },
    { value: "organic", label: "Organic / SEO", icon: "🌱" },
    { value: "referral", label: "Referral", icon: "🔗" },
  ];

const INTENT_LEVELS: {
  value: AudienceIntent;
  label: string;
  description: string;
}[] = [
  {
    value: "cold",
    label: "Cold",
    description: "Just discovered the brand, no prior awareness",
  },
  {
    value: "warm",
    label: "Warm",
    description: "Solution-aware, comparing options",
  },
  {
    value: "hot",
    label: "Hot",
    description: "High intent, ready to convert",
  },
];

interface Props {
  onSubmit: (context: AuditContext, input: { url?: string; html?: string }) => void;
  isLoading: boolean;
}

export default function AuditForm({ onSubmit, isLoading }: Props) {
  const [inputMode, setInputMode] = useState<"url" | "html">("url");
  const [url, setUrl] = useState("");
  const [html, setHtml] = useState("");
  const [conversionGoal, setConversionGoal] = useState(CONVERSION_GOALS[0]);
  const [customGoal, setCustomGoal] = useState("");
  const [trafficSource, setTrafficSource] = useState<TrafficSource>("paid-search");
  const [audienceIntent, setAudienceIntent] = useState<AudienceIntent>("cold");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const finalGoal =
      conversionGoal === "Custom…" ? customGoal : conversionGoal;
    if (!finalGoal.trim()) return;

    const context: AuditContext = {
      url: inputMode === "url" ? url : undefined,
      conversionGoal: finalGoal,
      trafficSource,
      audienceIntent,
    };

    const input =
      inputMode === "url"
        ? { url: url.trim() }
        : { html: html.trim() };

    onSubmit(context, input);
  };

  const isValid =
    (inputMode === "url" ? url.trim().length > 5 : html.trim().length > 50) &&
    (conversionGoal !== "Custom…" || customGoal.trim().length > 0);

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Input mode tabs */}
      <div>
        <div className="flex rounded-lg border border-slate-200 p-1 bg-slate-50 gap-1">
          {(["url", "html"] as const).map((mode) => (
            <button
              key={mode}
              type="button"
              onClick={() => setInputMode(mode)}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                inputMode === mode
                  ? "bg-white shadow-sm text-slate-900 border border-slate-200"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              {mode === "url" ? "🌐 Audit a URL" : "📋 Paste HTML"}
            </button>
          ))}
        </div>

        <div className="mt-3">
          {inputMode === "url" ? (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Landing page URL
              </label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/landing-page"
                className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 outline-none text-slate-900 placeholder-slate-400 transition-all"
                required={inputMode === "url"}
              />
              <p className="mt-1 text-xs text-slate-400">
                Page must be publicly accessible. If protected by Cloudflare, use HTML paste.
              </p>
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Paste page HTML
              </label>
              <textarea
                value={html}
                onChange={(e) => setHtml(e.target.value)}
                placeholder="Paste the full HTML source of the landing page here…"
                rows={6}
                className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 outline-none text-slate-900 placeholder-slate-400 transition-all font-mono text-xs resize-y"
                required={inputMode === "html"}
              />
              <p className="mt-1 text-xs text-slate-400">
                Right-click → View Page Source, then Ctrl+A and paste.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Conversion goal */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">
          Conversion goal
        </label>
        <select
          value={conversionGoal}
          onChange={(e) => setConversionGoal(e.target.value)}
          className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 outline-none text-slate-900 bg-white transition-all"
        >
          {CONVERSION_GOALS.map((goal) => (
            <option key={goal} value={goal}>
              {goal}
            </option>
          ))}
        </select>
        {conversionGoal === "Custom…" && (
          <input
            type="text"
            value={customGoal}
            onChange={(e) => setCustomGoal(e.target.value)}
            placeholder="Describe your conversion goal…"
            className="mt-2 w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 outline-none text-slate-900 placeholder-slate-400 transition-all"
          />
        )}
      </div>

      {/* Traffic source */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Traffic source
        </label>
        <div className="grid grid-cols-5 gap-2">
          {TRAFFIC_SOURCES.map((source) => (
            <button
              key={source.value}
              type="button"
              onClick={() => setTrafficSource(source.value)}
              className={`flex flex-col items-center gap-1 py-3 px-2 rounded-lg border text-xs font-medium transition-all ${
                trafficSource === source.value
                  ? "border-indigo-500 bg-indigo-50 text-indigo-700"
                  : "border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-50"
              }`}
            >
              <span className="text-lg">{source.icon}</span>
              <span className="text-center leading-tight">{source.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Audience intent */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Audience intent level
        </label>
        <div className="grid grid-cols-3 gap-2">
          {INTENT_LEVELS.map((level) => (
            <button
              key={level.value}
              type="button"
              onClick={() => setAudienceIntent(level.value)}
              className={`flex flex-col gap-1 py-3 px-3 rounded-lg border text-left transition-all ${
                audienceIntent === level.value
                  ? "border-indigo-500 bg-indigo-50"
                  : "border-slate-200 hover:border-slate-300 hover:bg-slate-50"
              }`}
            >
              <span
                className={`text-sm font-semibold ${
                  audienceIntent === level.value
                    ? "text-indigo-700"
                    : "text-slate-700"
                }`}
              >
                {level.label}
              </span>
              <span className="text-xs text-slate-500 leading-tight">
                {level.description}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={isLoading || !isValid}
        className="w-full py-4 px-6 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 disabled:text-slate-400 text-white font-semibold text-base transition-all shadow-sm hover:shadow-md disabled:shadow-none disabled:cursor-not-allowed"
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            Auditing…
          </span>
        ) : (
          "Run CRO Audit →"
        )}
      </button>
    </form>
  );
}
