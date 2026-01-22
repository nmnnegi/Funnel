export interface WorkItemConfig {
  _id?: string;
  uid: string;
  workflow_name: string;
  is_active: boolean;
  variables: FieldDefinition[];
  created_at?: string;
  updated_at?: string;
}

export interface WorkStage {
  _id?: string;
  uid: string;
  config: string;
  name: string;
  slug: string;
  color: string;
  description: string;
  order: number;
  is_active: boolean;
  allowed_next_stages: string[];
  stage_tasks: WorkStageTask[];
  created_at?: string;
  updated_at?: string;
}

export interface WorkStageTask {
  uid: string;
  name: string;
  description: string;
  required: boolean;
  order: number;
  task_variables: FieldDefinition[];
}

export interface WorkItem {
  _id?: string;
  uid: string;
  item_id: string;
  config: string;
  current_stage: string;
  status: string;
  name: string;
  email?: string;
  phone?: string;
  config_values: any[];
  assigned_to: string[];
  properties: Record<string, any>;
  linked_entities: Record<string, any>;
  history: any[];
  tasks: any[];
  activities: any[];
  created_at?: string;
  updated_at?: string;
  created_by?: string;
  
  // Legacy fields for backwards compatibility
  company?: string;
  stage?: string;
  priority?: 'low' | 'medium' | 'high';
  tags?: string[];
}

export interface StageData {
  entered_at: string;
  exited_at?: string;
  tasks_completed: Record<string, any>;
}

export interface Note {
  uid: string;
  content: string;
  created_by: string;
  created_at: string;
}

export interface FieldDefinition {
  field_key: string;
  label: string;
  field_type: FieldType;
  input_type: InputType;
  required: boolean;
  default_value?: any;
  options?: string[];
  validation_rules?: Record<string, any>;
  placeholder?: string;
  help_text?: string;
  order: number;
}

export const FieldType = {
  STRING: 'string',
  INTEGER: 'integer',
  DECIMAL: 'decimal',
  BOOLEAN: 'boolean',
  DATE: 'date',
  DATETIME: 'datetime',
  ENUM: 'enum',
  LIST: 'list',
  DICT: 'dict',
} as const;

export type FieldType = typeof FieldType[keyof typeof FieldType];

export const InputType = {
  TEXT: 'text',
  TEXTAREA: 'textarea',
  NUMBER: 'number',
  CHECKBOX: 'checkbox',
  RADIO: 'radio',
  DROPDOWN: 'dropdown',
  DATE_PICKER: 'date_picker',
  DATETIME_PICKER: 'datetime_picker',
  FILE_UPLOAD: 'file_upload',
} as const;

export type InputType = typeof InputType[keyof typeof InputType];

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
}
