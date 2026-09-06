/**
 * Lightweight client-side check so obviously bad input never reaches the
 * backend. The backend remains the source of truth for validation.
 */
export function isLikelyValidUrl(value: string): boolean {
  const trimmed = value.trim();
  if (!trimmed) return false;

  let parsed: URL;
  try {
    parsed = new URL(trimmed);
  } catch {
    return false;
  }

  if (parsed.protocol !== "http:" && parsed.protocol !== "https:") return false;
  if (!parsed.hostname || !parsed.hostname.includes(".")) return false;

  return true;
}
