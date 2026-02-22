"use client";

import { useRef } from "react";
import type { AuditReport } from "@/lib/types";
import ScoreGauge from "./ScoreGauge";
import SectionScores from "./SectionScores";
import RecommendationsList from "./RecommendationsList";
import CopyLab from "./CopyLab";
import ExperimentBacklog from "./ExperimentBacklog";
import SignalsPanel from "./SignalsPanel";

const SOURCE_LABELS: Record<string, string> = {
  "paid-search": "Paid Search",
  "paid-social": "Paid Social",
  email: "Email Campaign",
  organic: "Organic / SEO",
  referral: "Referral",
};

const INTENT_LABELS: Record<string, string> = {
  cold: "Cold",
  warm: "Warm",
  hot: "Hot",
};

interface Props {
  report: AuditReport;
  onReset: () => void;
}

export default function AuditReportView({ report, onReset }: Props) {
  const reportRef = useRef<HTMLDivElement>(null);

  const handlePrint = () => window.print();

  const auditedAt = new Date(report.createdAt).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div ref={reportRef} className="space-y-6 animate-fade-in">
      {/* Report header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Audit Report</h2>
          <p className="text-sm text-slate-500 mt-0.5">{auditedAt}</p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handlePrint}
            className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            Export PDF
          </button>
          <button
            type="button"
            onClick={onReset}
            className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 border border-indigo-100 rounded-lg hover:bg-indigo-100 transition-colors"
          >
            + New audit
          </button>
        </div>
      </div>

      {/* Context bar */}
      <div className="flex flex-wrap gap-2">
        {report.context.url && (
          <span className="text-xs bg-slate-100 text-slate-600 px-3 py-1 rounded-full truncate max-w-xs">
            🌐 {report.context.url}
          </span>
        )}
        <span className="text-xs bg-slate-100 text-slate-600 px-3 py-1 rounded-full">
          🎯 {report.context.conversionGoal}
        </span>
        <span className="text-xs bg-slate-100 text-slate-600 px-3 py-1 rounded-full">
          📡 {SOURCE_LABELS[report.context.trafficSource] || report.context.trafficSource}
        </span>
        <span className="text-xs bg-slate-100 text-slate-600 px-3 py-1 rounded-full">
          🎯 {INTENT_LABELS[report.context.audienceIntent]} intent
        </span>
      </div>

      {/* Score + Summary */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6">
        <div className="flex flex-col sm:flex-row items-center gap-6">
          <ScoreGauge score={report.overallScore} scoreBand={report.scoreBand} />
          <div className="flex-1">
            <h3 className="text-base font-bold text-slate-800 mb-2">
              Executive Summary
            </h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              {report.summary}
            </p>
          </div>
        </div>
      </div>

      {/* Section scores */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5">
        <h3 className="text-base font-bold text-slate-800 mb-4">
          Section Scores
        </h3>
        <SectionScores sections={report.sectionScores} />
      </div>

      {/* Top recommendations */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-bold text-slate-800">
            Top Recommendations
          </h3>
          <span className="text-xs text-slate-400">
            {report.topRecommendations.length} findings
          </span>
        </div>
        <RecommendationsList recommendations={report.topRecommendations} />
      </div>

      {/* Copy lab */}
      {report.copyRewrites.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <h3 className="text-base font-bold text-slate-800">Copy Lab</h3>
            <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full font-medium">
              AI rewrites
            </span>
          </div>
          <CopyLab rewrites={report.copyRewrites} />
        </div>
      )}

      {/* Experiment backlog */}
      {report.experimentIdeas.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <h3 className="text-base font-bold text-slate-800">
              Experiment Backlog
            </h3>
            <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full font-medium">
              A/B test ideas
            </span>
          </div>
          <ExperimentBacklog experiments={report.experimentIdeas} />
        </div>
      )}

      {/* Raw signals */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5">
        <SignalsPanel signals={report.signals} />
      </div>

      {/* Footer note */}
      <p className="text-xs text-slate-400 text-center pb-4">
        Audit powered by Claude · Scores are directional, not absolute ·{" "}
        <button
          type="button"
          onClick={onReset}
          className="text-indigo-500 hover:underline"
        >
          Run another audit
        </button>
      </p>
    </div>
  );
}
