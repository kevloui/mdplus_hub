export interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url: string | null;
  is_verified: boolean;
  created_at: string;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectDetail extends Project {
  owner: User;
  molecule_count: number;
  model_count: number;
}

export interface Molecule {
  id: string;
  name: string;
  description: string | null;
  project_id: string;
  molecule_type: "coarse_grained" | "atomistic" | "backmapped";
  file_format: "pdb" | "gro" | "xtc" | "dcd" | "mol2" | "xyz";
  n_atoms: number;
  n_frames: number;
  source_molecule_id: string | null;
  created_at: string;
}

export interface GlimpsModel {
  id: string;
  name: string;
  description: string | null;
  project_id: string;
  is_trained: boolean;
  training_config: Record<string, unknown> | null;
  training_metrics: Record<string, unknown> | null;
  cg_molecule_id: string | null;
  atomistic_molecule_id: string | null;
  trained_at: string | null;
  training_duration_seconds: number | null;
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: string;
  job_type: "training" | "inference" | "file_processing";
  status: "pending" | "queued" | "running" | "completed" | "failed" | "cancelled";
  project_id: string;
  model_id: string | null;
  progress_percent: number;
  progress_message: string | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
}
