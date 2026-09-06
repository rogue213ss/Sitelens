import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Search } from "lucide-react";
import { createScan, ApiError } from "../api";
import { isLikelyValidUrl } from "../lib/url";
import { LayerStack } from "../components/LayerStack";

export function Landing() {
  const navigate = useNavigate();
  const [url, setUrl] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    const trimmed = url.trim();
    if (!isLikelyValidUrl(trimmed)) {
      setError("Enter a full URL starting with http:// or https://");
      return;
    }

    setSubmitting(true);
    try {
      const scan = await createScan(trimmed);
      navigate(`/scan/${scan.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong creating the scan.");
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-base">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-accent" />
          <span className="font-mono text-sm tracking-tight text-text">sitelens</span>
        </div>
        <span className="font-mono text-xs text-text-dim">v0.1 · foundation</span>
      </header>

      <main className="mx-auto grid max-w-6xl grid-cols-1 items-center gap-16 px-6 pb-24 pt-12 md:grid-cols-[1.1fr_0.9fr] md:pt-20">
        <div>
          <h1 className="max-w-xl text-4xl font-semibold leading-[1.1] text-text sm:text-5xl">
            Understand how any website works.
          </h1>
          <p className="mt-5 max-w-lg text-base leading-relaxed text-text-muted">
            SiteLens analyzes the observable architecture, technology, network behavior,
            performance, and design of websites — then explains what it finds.
          </p>

          <form onSubmit={handleSubmit} className="mt-10 max-w-xl">
            <div
              className={`flex items-center gap-3 rounded-lg border bg-panel px-4 py-3.5 shadow-sm transition-colors ${
                error ? "border-danger" : "border-line focus-within:border-accent"
              }`}
            >
              <Search className="h-4 w-4 shrink-0 text-text-dim" strokeWidth={2} />
              <input
                type="text"
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                placeholder="https://example.com"
                className="w-full bg-transparent font-mono text-sm text-text placeholder:text-text-dim focus:outline-none"
                autoComplete="off"
                spellCheck={false}
              />
            </div>

            {error && <p className="mt-2 font-mono text-xs text-danger">{error}</p>}

            <button
              type="submit"
              disabled={submitting}
              className="mt-4 w-full rounded-lg bg-accent px-5 py-3 font-medium text-white shadow-sm transition-opacity hover:opacity-90 disabled:opacity-50 sm:w-auto"
            >
              {submitting ? "Starting scan…" : "Analyze website"}
            </button>
          </form>
        </div>

        <div className="flex justify-center md:justify-end">
          <LayerStack />
        </div>
      </main>

      <footer className="mx-auto max-w-6xl border-t border-line px-6 py-6">
        <p className="font-mono text-[11px] text-text-dim">
          Analysis reflects what is publicly observable from the outside. No private source,
          credentials, or backend systems are accessed.
        </p>
      </footer>
    </div>
  );
}
