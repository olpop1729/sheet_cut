// Mirrors the FastAPI schemas (sheetcut.api.schemas).

export interface ToolSpec {
  name: string;
  steplap_type: number;
  steplap_count: number;
  open_code: number;
  is_skewed: boolean;
}

export interface Profile {
  id: number;
  name: string;
  tools: ToolSpec[];
  pattern_type: number;
  steplap_tool_count: number;
  created_at: string;
  updated_at: string;
}

export interface RunParameters {
  length_list: number[];
  steplap_distances: number[];
  layers: number;
  start_sheet: number;
  scrap_length: number;
}

export interface GenerationSummary {
  id: number;
  profile_id: number | null;
  profile_name: string;
  pattern_type: number;
  parameters: RunParameters;
  row_count: number;
  pattern_length: number | null;
  sheet_count: number | null;
  artifact_path: string | null;
  created_at: string;
}

export interface GenerationDetail extends GenerationSummary {
  profile_snapshot: { name: string; tools: ToolSpec[] };
  machine_config: MachineConfigValues;
  start_index: number | null;
  end_index: number | null;
}

export interface StepsPage {
  generation_id: number;
  columns: string[];
  rows: (string | number | null)[][];
  total_rows: number;
  offset: number;
  limit: number;
}

export interface MachineConfigValues {
  offset_fp45: number;
  offset_fm45: number;
  offset_f0: number;
  offset_v_lat: number;
  distance_hole_vnotch: number;
  distance_shear_vnotch: number;
  coil_length: number;
}

export interface MachineConfigVersion {
  version: number;
  config: MachineConfigValues;
  comment: string;
  created_at: string;
}

export interface PlotEvent {
  row: number;
  tool: string | null;
  tool_number: number | null;
  feed: number;
  position: number;
  kind: "shear" | "hole" | "vnotch" | null;
  cut_x: number | null;
  v_travel: number | null;
}

export interface PieceEdge {
  tool: string;
  x: number;
  row: number;
}

export interface PieceHole {
  row: number;
  x: number;
  offset: number;
}

export interface PieceNotch extends PieceHole {
  travel: number | null;
}

export interface Piece {
  index: number;
  left: PieceEdge;
  right: PieceEdge;
  center_length: number;
  holes: PieceHole[];
  notches: PieceNotch[];
}

export interface PlotSeries {
  pattern_type: number;
  pattern_length: number | null;
  start_index: number | null;
  end_index: number | null;
  sheet_count: number | null;
  v_axis: number[];
  distances: { shear: number; hole: number; vnotch: number };
  events: PlotEvent[];
  pieces: Piece[];
}

export const PATTERN_NAMES: Record<number, string> = {
  1: "Side-limb yoke",
  2: "Split yoke",
  3: "Spear / central limb",
  4: "Symmetric fish",
  5: "Asymmetric fish",
};

export const TOOL_NAMES = ["fp45", "fm45", "f0", "v", "h", "s", "ys"] as const;

export const STEPLAP_TYPES: Record<number, string> = {
  0: "No step-lap",
  1: "Horizontal (longitudinal)",
  2: "Vertical (lateral)",
  3: "Skewed (lateral)",
};

export const OPEN_CODES: Record<number, string> = {
  0: "NA",
  1: "Open",
  2: "Closed",
  3: "Front open, rear open",
  4: "Front open, rear closed",
  5: "Front closed, rear open",
  6: "Front closed, rear closed",
  7: "Front open",
  8: "Front closed",
  9: "Rear open",
  10: "Rear closed",
};
