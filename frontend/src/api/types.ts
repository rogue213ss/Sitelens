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

export interface ScanPageInfo {
  requested_url: string;
  final_url: string;
  page_title: string;
  status_code: number;
  content_type: string | null;
  viewport: string | null;
  user_agent: string | null;
  html: string | null;
}

export interface ScanResults {
  id: string;
  status: ScanStatus;
  error: string | null;
  page: ScanPageInfo | null;
  links: any[];
  scripts: any[];
  stylesheets: any[];
  images: any[];
  network_requests: any[];
  performance: any | null;
  has_screenshot: boolean;
}
