/**
 * Types mirroring the backend schemas (`apps/server/src/schemas/*.py`), the same way
 * `sdk/ocr_sdk/schemas/` does for the Python SDK. Kept in sync by hand - see issue #509
 * for the audit that produced the Python side of this.
 */

export type TaskStatus
  = | 'created'
    | 'queued'
    | 'started'
    | 'in_progress'
    | 'completed'
    | 'failed'
    | 'retrying'
    | 'canceled'
    | 'timeout'

export type TaskOperation
  = | 'ocr'
    | 'default'
    | 'save_template'
    | 'forms'
    | 'vectorize'
    | 'docling'

export interface BaseBox {
  x: number
  y: number
  width: number
  height: number
  confidence: number
}

export interface Bbox extends BaseBox {
  text: string
  orientation?: number | null
}

export interface Checkbox extends BaseBox {
  is_checked: boolean
}

/** `src/schemas/layout.py::TableCell` */
export interface TableCell {
  /** 0-based index of the first row covered by the cell */
  row: number
  /** 0-based index of the first column covered by the cell */
  col: number
  rowspan: number
  colspan: number
  text: string
  is_header: boolean
  /** Normalized [xmin, ymin, xmax, ymax] on the page, when the model provides it */
  bbox?: number[] | null
}

/** `src/schemas/layout.py::TableContent` */
export interface TableContent {
  html: string
  markdown: string
  n_rows: number
  n_cols: number
  cells: TableCell[]
}

/** `src/schemas/layout.py::Layout` */
export interface Layout {
  cls_id: number
  label: string
  score: number
  /** [xmin, ymin, xmax, ymax] */
  coordinate: number[]
  content?: unknown
  /** Structured content, only for `table` regions */
  table?: TableContent | null
}

export interface RegionOfInterest {
  interest_zone: Bbox[]
  labels?: string | null
}

export interface InputForm {
  storage_file_path?: string | null
  raw_filename: string
  content_type: string
  ext: string
  size: number
  process_type?: string
  group_id?: string | null
  interest_zone?: RegionOfInterest[]
  source_url?: string | null
}

/** `src/schemas/template.py::FormEntry` */
export interface FormEntry {
  key: string
  value: string
  corrected_key?: string | null
  corrected_value?: string | null
}

/** `src/schemas/template.py::LLMFormField` */
export interface LLMFormField {
  name?: string | null
  value?: string | null
  type: string
  sections?: string[] | null
  filled?: boolean | null
}

export interface ImageFormDetector {
  is_form: boolean
  confidence: number
}

export interface Vector {
  id: string
  collection_name?: string | null
  model_name: string
  vector: number[]
  vector_size: number
  label: string
  source_id?: string | null
  page_num?: number | null
}

export interface Page {
  page: number
  page_url?: string | null
  boxes: Bbox[]
  layouts: Layout[]
  tables: Layout[]
  /** image / chart / seal regions (bbox only) */
  images: Layout[]
  /** formula regions (bbox only) */
  formulas: Layout[]
  checkboxes: Checkbox[]
  form_entries: (LLMFormField | FormEntry)[]
  image_form_detector?: ImageFormDetector | null
  vector?: Vector | null
  similar_template_ids: [string, number][]
  page_markdown?: string | null
}

export interface OCRResult {
  type: string
  model_name: string
  created_at: number
  updated_at: number
  version: string
  total_pages: number
  pages: Page[]
  extras?: Record<string, unknown> | null
  text?: string | null
}

export interface TaskModel {
  id: string
  user_id: string
  group_id?: string | null
  type: string
  status: TaskStatus | string
  percentage?: number | null
  input?: InputForm | null
  output?: OCRResult | null
  created_at: number
  updated_at: number
  extras?: Record<string, unknown> | null
  position?: number | null
  content_hash?: string | null
}

/** `src/schemas/pagination.py::Pagination` */
export interface Pagination<T> {
  total: number
  page: number
  page_size: number
  items: T[] | null
}

export type PaginatedTasks = Pagination<TaskModel>

export interface TaskStatsGlobal {
  total_tasks: number
  tasks_stats: Record<string, number>
}

export interface TaskStatsUser extends TaskStatsGlobal {
  user_id: string
}

export interface TaskStats {
  global_stats: TaskStatsGlobal
  user_stats: TaskStatsUser
}

export interface Health {
  name: string
  version: string
  up_time: string
  status?: string | null
  extras?: Record<string, unknown> | null
  dependencies?: Health[] | null
}

/** `PUT /process` response item - SDK-only shape, not a single backend pydantic model. */
export interface ProcessResponse {
  page_content: string
  metadata: Record<string, unknown>
}

export type TaskValueTransform = 'text' | 'form' | 'form-csv' | 'only-result'

/**
 * Progress of the layout detection, in `task.extras.layout_status`.
 * `partial`: regions are available, the table structure is still being computed.
 */
export type LayoutStatus = 'pending' | 'partial' | 'completed' | 'failed' | 'skipped'
