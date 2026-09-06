export type ScanStatus = "QUEUED" | "RUNNING" | "COMPLETE" | "FAILED";

export interface Scan {
  id: string;
  url: string;
  normalized_url: string;
  status: ScanStatus;
  created_at: string;
  completed_at: string | null;
  error: string | null;
}

export interface ScanStatusInfo {
  id: string;
  status: ScanStatus;
  error: string | null;
}
