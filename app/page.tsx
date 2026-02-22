"use client";

import { useState } from "react";
import AuditForm from "@/components/AuditForm";
import AuditReportView from "@/components/AuditReport";
import type { AuditContext, AuditReport } from "@/lib/types";

type AuditState =
  | { status: "idle" }
  | { status: "loading"; step: string }
  | { status: "done"; report: AuditReport }
  | { status: "error"; message: string };

const LOADING_STEPS = [
  "Fetching page content…",
  "Extracting CRO signals…",
  "Running AI analysis…",
  "Scoring and generating recommendations…",
];

export default function HomePage() {
  const [state, setState] = useState<AuditState>({ status: "idle" });
  const [stepIndex, setStepIndex] = useState(0);

  const handleSubmit = async (
    context: AuditContext,
    input: { url?: string; html?: string }
  ) => {
    setState({ status: "loading", step: LOADING_STEPS[0] });
    setStepIndex(0);

    // Cycle through loading steps to give visual feedback
    const interval = setInterval(() => {
      setStepIndex((prev) => {
        const next = prev + 1;
        if (next >= LOADING_STEPS.length) {
          clearInterval(interval);
          return prev;
        }
        setState({ status: "loading", step: LOADING_STEPS[next] });
        return next;
      });
    }, 4000);

    try {
      const res = await fetch("/api/audit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...input, context }),
      });

      clearInterval(interval);

      const data = await res.json();

      if (!res.ok || data.error) {
        setState({ status: "error", message: data.error || "Audit failed." });
        return;
      }

      setState({ status: "done", report: data.report });

      // Scroll to results
      setTimeout(() => {
        document
          .getElementById("results")
          ?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (err) {
      clearInterval(interval);
      setState({
        status: "error",
        message:
          err instanceof Error ? err.message : "Network error. Please retry.",
      });
    }
  };

  const handleReset = () => {
    setState({ status: "idle" });
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      {/* Hero */}
      {state.status === "idle" && (
        <div className="text-center mb-10 animate-fade-in">
          <div className="inline-flex items-center gap-2 bg-indigo-50 text-indigo-700 text-sm font-medium px-4 py-1.5 rounded-full border border-indigo-100 mb-5">
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
            AI-powered landing page analysis
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 leading-tight mb-4">
            Audit your landing page.
            <br />
            <span className="text-indigo-600">Fix what kills conversions.</span>
          </h1>
          <p className="text-lg text-slate-500 max-w-2xl mx-auto">
            Paste a URL and get an evidence-based CRO score, ranked
            recommendations, AI-rewritten copy, and A/B test ideas — in under a
            minute.
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 items-start">
        {/* Form column */}
        <div
          className={`${
            state.status === "done" ? "lg:col-span-2" : "lg:col-span-3 mx-auto w-full max-w-2xl"
          }`}
        >
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            {state.status !== "done" ? (
              <>
                <h2 className="text-lg font-bold text-slate-800 mb-5">
                  Start your audit
                </h2>
                <AuditForm
                  onSubmit={handleSubmit}
                  isLoading={state.status === "loading"}
                />

                {/* Loading state */}
                {state.status === "loading" && (
                  <div className="mt-5 p-4 bg-indigo-50 border border-indigo-100 rounded-xl">
                    <div className="flex items-center gap-3">
                      <div className="w-5 h-5 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin shrink-0" />
                      <p className="text-sm text-indigo-700 font-medium">
                        {LOADING_STEPS[stepIndex]}
                      </p>
                    </div>
                    <div className="mt-3 flex gap-1">
                      {LOADING_STEPS.map((_, i) => (
                        <div
                          key={i}
                          className={`h-1 rounded-full flex-1 transition-all duration-500 ${
                            i <= stepIndex ? "bg-indigo-500" : "bg-indigo-200"
                          }`}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Error state */}
                {state.status === "error" && (
                  <div className="mt-5 p-4 bg-red-50 border border-red-200 rounded-xl">
                    <div className="flex items-start gap-2">
                      <svg
                        className="w-5 h-5 text-red-500 shrink-0 mt-0.5"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      <p className="text-sm text-red-700">{state.message}</p>
                    </div>
                  </div>
                )}
              </>
            ) : (
              /* Compact form reminder when results are shown */
              <div>
                <h2 className="text-sm font-bold text-slate-700 mb-1">
                  Audit settings
                </h2>
                <div className="space-y-1 text-xs text-slate-500">
                  <p>
                    Goal:{" "}
                    <span className="font-medium text-slate-700">
                      {state.report.context.conversionGoal}
                    </span>
                  </p>
                  <p>
                    Source:{" "}
                    <span className="font-medium text-slate-700">
                      {state.report.context.trafficSource}
                    </span>
                  </p>
                  <p>
                    Intent:{" "}
                    <span className="font-medium text-slate-700">
                      {state.report.context.audienceIntent}
                    </span>
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleReset}
                  className="mt-3 w-full py-2 text-sm font-medium text-indigo-600 bg-indigo-50 border border-indigo-100 rounded-lg hover:bg-indigo-100 transition-colors"
                >
                  + New audit
                </button>
              </div>
            )}
          </div>

          {/* Feature highlights (only when idle) */}
          {state.status === "idle" && (
            <div className="mt-5 grid grid-cols-3 gap-3">
              {[
                { icon: "🎯", title: "Evidence-based", desc: "Every finding cites page data" },
                { icon: "✍️", title: "Copy rewrites", desc: "AI-improved headline & CTAs" },
                { icon: "🧪", title: "A/B test ideas", desc: "Ready-to-run experiment cards" },
              ].map((f) => (
                <div
                  key={f.title}
                  className="bg-white border border-slate-200 rounded-xl p-3 text-center"
                >
                  <div className="text-2xl mb-1">{f.icon}</div>
                  <p className="text-xs font-semibold text-slate-700">{f.title}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{f.desc}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Results column */}
        {state.status === "done" && (
          <div id="results" className="lg:col-span-3 animate-slide-up">
            <AuditReportView report={state.report} onReset={handleReset} />
          </div>
        )}
      </div>

      {/* Example / social proof (only idle) */}
      {state.status === "idle" && (
        <div className="mt-16 text-center">
          <p className="text-sm text-slate-400 mb-6">
            Works with any publicly accessible landing page
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-3xl mx-auto">
            {[
              {
                type: "Lead gen",
                desc: "Book a call, get a quote, free trial",
                icon: "📞",
              },
              {
                type: "Ecommerce",
                desc: "Product pages, limited-time offers",
                icon: "🛒",
              },
              {
                type: "SaaS",
                desc: "Feature pages, pricing, signup flows",
                icon: "💻",
              },
            ].map((t) => (
              <div
                key={t.type}
                className="bg-white border border-slate-200 rounded-xl p-4 text-left"
              >
                <div className="text-2xl mb-2">{t.icon}</div>
                <p className="text-sm font-semibold text-slate-800">{t.type}</p>
                <p className="text-xs text-slate-500 mt-1">{t.desc}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
