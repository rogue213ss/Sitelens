import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getScan, ApiError, type Scan } from "../api";

const PIPELINE_STEPS = [
  "Browser session",
  "Website capture",
  "Technology analysis",
  "Network analysis",
  "Architecture analysis",
  "AI synthesis",
];

export function ScanPage() {
  const { scanId } = useParams<{ scanId: string }>();
  const [scan, setScan] = useState<Scan | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!scanId) return;

    let cancelled = false;
    getScan(scanId)
      .then((result) => {
        if (!cancelled) setScan(result);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err instanceof ApiError ? err.message : "Couldn't load this scan.");
      });

    return () => {
      cancelled = true;
    };
  }, [scanId]);

  return (
    <div className="min-h-screen bg-base bg-grid">
      <header className="mx-auto flex max-w-3xl items-center justify-between px-6 py-6">
        <Link to="/" className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-accent" />
          <span className="font-mono text-sm tracking-tight text-text">sitelens</span>
        </Link>
        {scan && <span className="font-mono text-xs text-text-dim">{scan.id}</span>}
      </header>

      <main className="mx-auto max-w-3xl px-6 py-16">
        {error && (
          <div className="rounded-lg border border-danger/30 bg-panel px-5 py-4 shadow-sm">
            <p className="font-mono text-sm text-danger">{error}</p>
          </div>
        )}

        {!error && (
          <div className="rounded-xl border border-line bg-panel px-6 py-8 shadow-sm sm:px-10 sm:py-10">
            <p className="font-mono text-xs uppercase tracking-wider text-text-dim">Site analysis</p>
            <h1 className="mt-3 text-2xl font-semibold text-text sm:text-3xl">
              {scan ? "Preparing SiteLens…" : "Loading scan…"}
            </h1>
            {scan && (
              <p className="mt-2 break-all font-mono text-sm text-text-muted">{scan.normalized_url}</p>
            )}

            <ul className="mt-8 flex flex-col gap-3">
              {PIPELINE_STEPS.map((step) => (
                <li key={step} className="flex items-center gap-3 font-mono text-sm text-text-muted">
                  <span className="inline-block h-2.5 w-2.5 shrink-0 rounded-full border border-line" />
                  {step}
                </li>
              ))}
            </ul>

            <div className="mt-8 flex items-center gap-3 border-t border-line pt-6">
              <span className="rounded-full border border-line bg-accent-soft px-2.5 py-1 font-mono text-[11px] text-accent">
                status: {scan?.status ?? "…"}
              </span>
              <p className="font-mono text-[11px] text-text-dim">
                This pipeline isn't built yet — analysis hasn't started.
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
