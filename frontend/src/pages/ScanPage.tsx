import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getScan, getScanStatus, getScanResults, ApiError, type Scan, type ScanResults, type ScanStatus } from "../api";

const PIPELINE_STEPS = [
  "Browser session",
  "Website capture",
  "Resource collection",
  "Network capture",
  "Performance capture",
  "Finalizing",
];

export function ScanPage() {
  const { scanId } = useParams<{ scanId: string }>();
  const [scan, setScan] = useState<Scan | null>(null);
  const [status, setStatus] = useState<ScanStatus | null>(null);
  const [results, setResults] = useState<ScanResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!scanId) return;

    let cancelled = false;
    
    // Initial fetch
    getScan(scanId)
      .then((result) => {
        if (cancelled) return;
        setScan(result);
        setStatus(result.status);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err instanceof ApiError ? err.message : "Couldn't load this scan.");
      });

    return () => {
      cancelled = true;
    };
  }, [scanId]);

  // Polling effect
  useEffect(() => {
    if (!scanId || !status || status === "COMPLETE" || status === "FAILED") {
      return;
    }

    const interval = setInterval(() => {
      getScanStatus(scanId)
        .then((res) => {
          setStatus(res.status);
          if (res.error) {
            setError(res.error);
          }
        })
        .catch(() => {});
    }, 2000);

    return () => clearInterval(interval);
  }, [scanId, status]);

  // Fetch results when complete
  useEffect(() => {
    if (status === "COMPLETE" && scanId && !results) {
      getScanResults(scanId)
        .then(setResults)
        .catch((err) => setError(err instanceof ApiError ? err.message : "Couldn't load results."));
    }
  }, [status, scanId, results]);

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
          <div className="rounded-lg border border-danger/30 bg-panel px-5 py-4 shadow-sm mb-6">
            <p className="font-mono text-sm text-danger">{error}</p>
          </div>
        )}

        {!results && !error && (
          <div className="rounded-xl border border-line bg-panel px-6 py-8 shadow-sm sm:px-10 sm:py-10">
            <p className="font-mono text-xs uppercase tracking-wider text-text-dim">Site analysis</p>
            <h1 className="mt-3 text-2xl font-semibold text-text sm:text-3xl">
              {status === "QUEUED" ? "Scan queued…" : status === "RUNNING" ? "Running scan…" : "Loading…"}
            </h1>
            {scan && (
              <p className="mt-2 break-all font-mono text-sm text-text-muted">{scan.normalized_url}</p>
            )}

            <ul className="mt-8 flex flex-col gap-3">
              {PIPELINE_STEPS.map((step, idx) => {
                let stepStatus = "pending";
                if (status === "COMPLETE") stepStatus = "done";
                else if (status === "RUNNING" && idx === 0) stepStatus = "active";
                
                return (
                  <li key={step} className="flex items-center gap-3 font-mono text-sm text-text-muted">
                    <span className={`inline-block h-2.5 w-2.5 shrink-0 rounded-full border border-line ${stepStatus === "active" ? "bg-accent border-accent" : stepStatus === "done" ? "bg-text border-text" : ""}`} />
                    <span className={stepStatus === "active" ? "text-text font-medium" : ""}>{step}</span>
                  </li>
                );
              })}
            </ul>

            <div className="mt-8 flex items-center gap-3 border-t border-line pt-6">
              <span className={`rounded-full border px-2.5 py-1 font-mono text-[11px] ${status === "FAILED" ? "border-danger bg-danger/10 text-danger" : "border-line bg-accent-soft text-accent"}`}>
                status: {status ?? "…"}
              </span>
            </div>
          </div>
        )}

        {results && (
          <div className="space-y-6">
            <div className="rounded-xl border border-line bg-panel px-6 py-8 shadow-sm sm:px-10 sm:py-10">
              <p className="font-mono text-xs uppercase tracking-wider text-text-dim">Scan complete</p>
              <h1 className="mt-3 text-2xl font-semibold text-text sm:text-3xl">
                {results.page?.page_title || "Untitled Page"}
              </h1>
              <p className="mt-2 break-all font-mono text-sm text-text-muted">
                {results.page?.final_url || scan?.normalized_url}
              </p>
              
              <div className="mt-6 flex items-center gap-4">
                 <span className={`rounded-full border px-2.5 py-1 font-mono text-[11px] ${results.page?.status_code && results.page.status_code >= 400 ? "border-danger bg-danger/10 text-danger" : "border-line bg-green-500/10 text-green-500"}`}>
                  HTTP {results.page?.status_code || "Unknown"}
                 </span>
                 <span className="rounded-full border border-line bg-accent-soft px-2.5 py-1 font-mono text-[11px] text-accent">
                  status: COMPLETE
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              {[
                { label: "Links", value: results.links.length },
                { label: "Scripts", value: results.scripts.length },
                { label: "Stylesheets", value: results.stylesheets.length },
                { label: "Images", value: results.images.length },
                { label: "Network Requests", value: results.network_requests.length },
              ].map(stat => (
                <div key={stat.label} className="rounded-xl border border-line bg-panel p-5 text-center shadow-sm">
                  <div className="text-2xl font-semibold text-text">{stat.value}</div>
                  <div className="mt-1 font-mono text-[10px] uppercase text-text-dim">{stat.label}</div>
                </div>
              ))}
            </div>

            {results.has_screenshot && (
              <div className="rounded-xl border border-line bg-panel overflow-hidden shadow-sm">
                <div className="border-b border-line px-5 py-3 bg-panel-dark">
                  <span className="font-mono text-xs uppercase text-text-dim">Screenshot</span>
                </div>
                <div className="p-4 bg-base">
                  <img 
                    src={`/api/scans/${scanId}/screenshot`} 
                    alt="Page screenshot" 
                    className="w-full h-auto rounded border border-line shadow-sm"
                  />
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
