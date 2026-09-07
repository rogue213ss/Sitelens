import { request } from "./client";
import type { Scan, ScanStatusInfo, ScanResults } from "./types";

export function createScan(url: string): Promise<Scan> {
  return request<Scan>("/api/scans", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
}

export function getScan(scanId: string): Promise<Scan> {
  return request<Scan>(`/api/scans/${scanId}`);
}

export function getScanStatus(scanId: string): Promise<ScanStatusInfo> {
  return request<ScanStatusInfo>(`/api/scans/${scanId}/status`);
}

export function getScanResults(scanId: string): Promise<ScanResults> {
  return request<ScanResults>(`/api/scans/${scanId}/results`);
}
