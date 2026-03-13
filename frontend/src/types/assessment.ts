export interface ReportRisk {
  title: string;
  detail: string;
}

export interface PriorityStage {
  name: string;
  reason: string;
}

export interface ReportData {
  readiness_level: 'early' | 'developing' | 'ready';
  readiness_summary: string;
  priority_stage: PriorityStage;
  top_risks: ReportRisk[];
  first_30_days: string[];
  one_line_verdict: string;
}
