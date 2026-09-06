const LAYERS = [
  { label: "Design", detail: "Layout, type, color system" },
  { label: "Performance", detail: "Load timing, asset weight" },
  { label: "Network", detail: "Requests, endpoints, headers" },
  { label: "Technology", detail: "Frameworks, libraries, hosting" },
  { label: "Structure", detail: "Pages, routes, DOM shape" },
];

/**
 * Decorative cross-section of the layers SiteLens will eventually observe.
 * Purely illustrative in Part 1 - no analysis happens yet.
 */
export function LayerStack() {
  return (
    <div className="relative w-full max-w-sm">
      <div className="flex flex-col gap-2">
        {LAYERS.map((layer, index) => (
          <div
            key={layer.label}
            className="group relative rounded-md border border-line bg-panel px-4 py-3 shadow-sm transition-colors hover:border-accent"
            style={{ marginLeft: `${index * 14}px` }}
          >
            <div className="flex items-baseline justify-between gap-4">
              <span className="font-mono text-sm text-text">{layer.label}</span>
              <span className="font-mono text-[11px] text-cyan">0{LAYERS.length - index}</span>
            </div>
            <p className="mt-1 font-mono text-[11px] text-text-muted">{layer.detail}</p>
          </div>
        ))}
      </div>
      <div className="pointer-events-none absolute -left-3 top-0 h-full w-px bg-gradient-to-b from-transparent via-line to-transparent" />
    </div>
  );
}
