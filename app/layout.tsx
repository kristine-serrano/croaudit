import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CROAudit — AI Landing Page Audit",
  description:
    "Get an AI-powered CRO audit of any landing page in seconds. Score, fix, and test your way to higher conversions.",
  openGraph: {
    title: "CROAudit — AI Landing Page Audit",
    description:
      "Score your landing page on messaging, CTAs, trust, and friction. Powered by Claude.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50">
        {/* Top nav */}
        <nav className="border-b border-slate-200 bg-white sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center">
                <svg
                  className="w-4 h-4 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <span className="font-bold text-slate-900">CROAudit</span>
              <span className="text-xs text-white bg-indigo-500 px-2 py-0.5 rounded-full font-medium">
                MVP
              </span>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <span>Powered by</span>
              <span className="font-semibold text-slate-700">Claude</span>
            </div>
          </div>
        </nav>

        {/* Main */}
        <main>{children}</main>

        {/* Footer */}
        <footer className="border-t border-slate-200 mt-16 py-8 text-center no-print">
          <p className="text-sm text-slate-400">
            CROAudit · AI-powered landing page analysis · Scores are
            directional, not absolute
          </p>
        </footer>
      </body>
    </html>
  );
}
