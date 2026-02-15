export interface Vitals {
  hr?: number;
  bp?: string;
  temp?: number;
}

export interface SpecialistData {
  [key: string]: string | null;
}

export interface PatientState {
  chief_complaint?: string;
  vitals?: Vitals;
  medication?: string;
  is_red_alert?: boolean;
  meta?: {
    active_protocol: string;
    vision_source?: string;
    clinical_markers?: string[];
  };
  specialist_data?: SpecialistData;
}

export interface CompressionResult {
  original_text: string;
  compressed_state: PatientState;
  original_token_count: number;
  compressed_token_count: number;
  reduction_percentage: number;
  compression_time_ms: number;
}

export interface TriageResult {
  priority_level: "P1" | "P2" | "P3";
  priority_name: "CRITICAL" | "URGENT" | "STANDARD";
  reason: string;
}

export interface DoctorResult {
  recommendation: string;
  processing_time_ms: number;
}

export interface PipelineResult {
  compression: CompressionResult;
  triage: TriageResult;
  doctor: DoctorResult;
  total_time_ms: number;
}
