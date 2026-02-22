import { NextRequest, NextResponse } from "next/server";
import { extractSignals } from "@/lib/extractor";
import { analyzeWithClaude } from "@/lib/analyzer";
import type { AuditRequest } from "@/lib/types";

export const maxDuration = 60;

export async function POST(req: NextRequest) {
  try {
    const body = (await req.json()) as AuditRequest;
    const { url, html, context } = body;

    if (!context?.conversionGoal) {
      return NextResponse.json(
        { error: "Conversion goal is required." },
        { status: 400 }
      );
    }

    if (!url && !html) {
      return NextResponse.json(
        { error: "Either a URL or HTML content is required." },
        { status: 400 }
      );
    }

    let pageHtml = "";
    let pageUrl = url || "";

    if (url) {
      // Validate URL
      try {
        new URL(url);
      } catch {
        return NextResponse.json(
          { error: "Invalid URL — please include https://" },
          { status: 400 }
        );
      }

      // Fetch the page server-side (no CORS issues)
      let fetchResponse: Response;
      try {
        fetchResponse = await fetch(url, {
          headers: {
            "User-Agent":
              "Mozilla/5.0 (compatible; CROAuditBot/1.0; +https://croaudit.app)",
            Accept:
              "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
          },
          signal: AbortSignal.timeout(30000),
          redirect: "follow",
        });
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Unknown fetch error";
        return NextResponse.json(
          {
            error: `Could not reach the URL: ${message}. Try pasting the HTML instead.`,
          },
          { status: 400 }
        );
      }

      if (!fetchResponse.ok) {
        return NextResponse.json(
          {
            error: `The page returned status ${fetchResponse.status}. It may be protected. Try pasting the HTML instead.`,
          },
          { status: 400 }
        );
      }

      const contentType = fetchResponse.headers.get("content-type") || "";
      if (!contentType.includes("html")) {
        return NextResponse.json(
          { error: "URL does not return an HTML page." },
          { status: 400 }
        );
      }

      pageHtml = await fetchResponse.text();
    } else if (html) {
      pageHtml = html;
    }

    if (!pageHtml || pageHtml.length < 100) {
      return NextResponse.json(
        { error: "Page content is too short or empty to audit." },
        { status: 400 }
      );
    }

    // Extract CRO signals from HTML
    const signals = extractSignals(pageHtml, pageUrl);

    // Analyze with Claude
    const analysis = await analyzeWithClaude(signals, context);

    const report = {
      ...analysis,
      signals,
      context,
      createdAt: new Date().toISOString(),
    };

    return NextResponse.json({ report });
  } catch (err) {
    console.error("[audit] error:", err);
    const message = err instanceof Error ? err.message : "Audit failed";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
