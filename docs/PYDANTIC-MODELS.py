"""
Complete Pydantic Models for Lead CRM (MongoDB Schema)

This file contains all Pydantic models needed for the standalone Lead CRM.
These models define the schema for MongoDB documents and provide validation.

Collection: leads (Single collection for everything)
Document Types:
- type="lead"    : Lead/WorkItem documents
- type="stage"   : Stage configuration documents
- type="config"  : Single workflow configuration document
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum


# ═══════════════════════════════════════════════════════════
# Custom Types & Enums
# ═══════════════════════════════════════════════════════════

class PyObjectId(ObjectId):
    """Custom ObjectId validator for Pydantic v2"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class WorkItemTaskStatus(str, Enum):
    """Status of a task in the workflow"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class WorkItemStatus(str, Enum):
    """Status of a work item (lead)"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class FieldType(str, Enum):
    """Data types for custom fields"""
    STRING = "string"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ENUM = "enum"
    ARRAY = "array"
    DOCUMENT = "document"


class ArrayItemType(str, Enum):
    """Data types for array items"""
    STRING = "string"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ENUM = "enum"
    DOCUMENT = "document"


class InputType(str, Enum):
    """UI widget types for rendering form inputs"""
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    DROPDOWN = "dropdown"
    MULTI_SELECT = "multi_select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    DATE_PICKER = "date_picker"
    DATETIME_PICKER = "datetime_picker"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    FILE_UPLOAD = "file_upload"


# ═══════════════════════════════════════════════════════════
# Field Definition Models
# ═══════════════════════════════════════════════════════════

class FieldDefinition(BaseModel):
    """
    Reusable field definition for custom fields.
    Used in:
    - WorkItemConfig.variables (global lead fields)
    - WorkStageTask.task_variables (task-specific fields)
    
    Example:
    {
        "field_key": "budget",
        "label": "Budget",
        "field_type": "decimal",
        "input_type": "number",
        "required": true,
        "placeholder": "Enter budget amount",
        "validation_rules": {"min": 1000, "max": 1000000}
    }
    """
    field_key: str  # Unique identifier (e.g., "budget", "lead_source")
    label: str  # Display name (e.g., "Budget", "Lead Source")
    field_type: FieldType  # Data type
    input_type: InputType  # UI widget type
    required: bool = False  # Is this field required?
    options: List[str] = Field(default_factory=list)  # Options for enum/dropdown
    default_value: Optional[str] = None  # Default value
    validation_rules: Dict[str, Any] = Field(default_factory=dict)  # Custom validation
    placeholder: str = ""  # Placeholder text
    help_text: str = ""  # Help text
    order: int = 0  # Display order
    is_active: bool = True  # Is this field active?
    array_item_type: Optional[ArrayItemType] = None  # Type for array items

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "field_key": "budget",
                "label": "Budget",
                "field_type": "decimal",
                "input_type": "number",
                "required": True,
                "placeholder": "Enter budget amount",
                "validation_rules": {"min": 1000, "max": 1000000}
            }
        }


class FieldValueBase(BaseModel):
    """
    Base model for storing field values.
    Stores both original (string) and parsed (typed) values.
    
    Example:
    {
        "variable": "budget",
        "field_type": "decimal",
        "original_value": "50000",
        "value": 50000.0
    }
    """
    variable: str  # field_key reference
    field_type: FieldType  # Data type
    original_value: str = ""  # Original string value (source of truth)
    value: Any = None  # Parsed/typed value

    class Config:
        populate_by_name = True


class TaskFieldValue(FieldValueBase):
    """Field value for task variables (collected during task completion)"""
    pass


class ConfigFieldValue(FieldValueBase):
    """Field value for lead config variables (global custom fields)"""
    pass


# ═══════════════════════════════════════════════════════════
# Task Models
# ═══════════════════════════════════════════════════════════

class WorkStageTask(BaseModel):
    """
    Task template attached to a stage.
    When a lead enters this stage, instances of these tasks are created.
    
    Example:
    {
        "uid": "task-initial-contact",
        "name": "Initial Contact",
        "description": "Reach out to the lead",
        "required": true,
        "order": 0,
        "task_variables": [
            {
                "field_key": "contact_method",
                "label": "Contact Method",
                "field_type": "enum",
                "input_type": "dropdown",
                "options": ["Email", "Phone", "Social Media"],
                "required": true
            }
        ]
    }
    """
    uid: str  # Unique task template ID
    name: str  # Task name
    description: Optional[str] = None
    required: bool = False  # Must complete before stage transition?
    order: int = 0  # Display order
    is_active: bool = True
    task_variables: List[FieldDefinition] = Field(default_factory=list)  # Fields to collect

    class Config:
        populate_by_name = True


class WorkItemTask(BaseModel):
    """
    Task instance created when a lead enters a stage.
    Tracks completion status and collected field values.
    
    Example:
    {
        "uid": "task-inst-123",
        "template_id": "task-initial-contact",
        "stage": "stage-new-lead",
        "name": "Initial Contact",
        "status": "completed",
        "completed_at": "2026-01-21T11:00:00Z",
        "completed_by": "user-xyz",
        "notes": "Contact established via email",
        "field_values": [
            {
                "variable": "contact_method",
                "field_type": "enum",
                "original_value": "email",
                "value": "email"
            }
        ]
    }
    """
    uid: str  # Unique task instance ID
    name: str
    description: Optional[str] = None
    template_id: str  # Reference to WorkStageTask.uid
    stage: str  # Stage UID where this task was created
    status: WorkItemTaskStatus = WorkItemTaskStatus.PENDING
    required: bool = False
    order: int = 0
    is_active: bool = True
    task_variables: List[FieldDefinition] = Field(default_factory=list)
    completed_at: Optional[datetime] = None
    completed_by: Optional[str] = None  # User ID who completed
    notes: str = ""
    field_values: List[TaskFieldValue] = Field(default_factory=list)

    class Config:
        json_encoders = {ObjectId: str}


# ═══════════════════════════════════════════════════════════
# Stage Model
# ═══════════════════════════════════════════════════════════

class WorkStage(BaseModel):
    """
    Stage definition in the workflow pipeline.
    Stored in MongoDB with type="stage".
    
    Example:
    {
        "_id": ObjectId("..."),
        "type": "stage",
        "uid": "stage-new-lead",
        "name": "New Lead",
        "slug": "new-lead",
        "color": "#3B82F6",
        "description": "Initial stage for new leads",
        "order": 0,
        "is_active": true,
        "allowed_next_stages": ["stage-contacted"],
        "stage_tasks": [
            {
                "uid": "task-initial-contact",
                "name": "Initial Contact",
                "required": true,
                "task_variables": [...]
            }
        ],
        "created_at": "2026-01-21T00:00:00Z",
        "updated_at": "2026-01-21T00:00:00Z"
    }
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    type: str = "stage"  # Document type discriminator
    uid: str  # Unique stage ID
    name: str  # Stage name (e.g., "New Lead", "Contacted")
    slug: str  # URL-friendly slug (e.g., "new-lead", "contacted")
    color: str = "#6B7280"  # Hex color for UI
    description: Optional[str] = None
    order: int = 0  # Display order in Kanban (0 = leftmost)
    is_active: bool = True
    allowed_next_stages: List[str] = Field(default_factory=list)  # UIDs of allowed next stages
    stage_tasks: List[WorkStageTask] = Field(default_factory=list)  # Task templates
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ═══════════════════════════════════════════════════════════
# Activity & History Models
# ═══════════════════════════════════════════════════════════

class Activity(BaseModel):
    """
    Activity log entry for audit trail.
    Tracks all changes to the lead (stage changes, task completions, field updates, etc.).
    
    Example:
    {
        "type": "STAGE_CHANGE",
        "subject": "Lead moved to Contacted",
        "description": "Successfully reached out via email",
        "performed_by": "user-xyz",
        "created_at": "2026-01-21T11:00:00Z",
        "created_by": "user-xyz",
        "activity_data": {
            "from_stage": "New Lead",
            "to_stage": "Contacted",
            "comment": "Email sent and replied"
        }
    }
    
    Activity Types:
    - CREATED: Lead created
    - STAGE_CHANGE: Stage transition
    - TASK_COMPLETED: Task completed
    - FIELD_UPDATED: Custom field updated
    - ASSIGNED: Lead assigned to user
    - NOTE_ADDED: Manual note added
    """
    type: str  # STAGE_CHANGE, TASK_COMPLETED, FIELD_UPDATED, CREATED, ASSIGNED, etc.
    subject: str  # Human-readable summary
    description: Optional[str] = None  # Additional details
    performed_by: Optional[str] = None  # User ID who performed action
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # User ID (usually same as performed_by)
    activity_data: Dict[str, Any] = Field(default_factory=dict)  # Additional metadata

    class Config:
        json_encoders = {ObjectId: str}


class HistoryData(BaseModel):
    """
    Stage transition history entry.
    Tracks when lead entered and exited each stage.
    
    Example:
    {
        "stage": "stage-new-lead",
        "entered_at": "2026-01-21T10:00:00Z",
        "exited_at": "2026-01-21T11:00:00Z"
    }
    """
    stage: str  # Stage UID
    entered_at: datetime = Field(default_factory=datetime.utcnow)
    exited_at: Optional[datetime] = None  # Null if still in this stage

    class Config:
        json_encoders = {ObjectId: str}


# ═══════════════════════════════════════════════════════════
# Work Item (Lead) Model
# ═══════════════════════════════════════════════════════════

class WorkItem(BaseModel):
    """
    Main Lead document (WorkItem).
    Stored in MongoDB with type="lead".
    Contains all lead data, tasks, activities, and history.
    
    Example:
    {
        "_id": ObjectId("..."),
        "type": "lead",
        "uid": "uid-abc123",
        "item_id": "LEAD-202601-00001",
        "current_stage": "stage-new-lead",
        "status": "pending",
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "config": "default",
        "config_values": [
            {
                "variable": "budget",
                "field_type": "decimal",
                "original_value": "50000",
                "value": 50000.0
            },
            {
                "variable": "lead_source",
                "field_type": "enum",
                "original_value": "Website",
                "value": "Website"
            }
        ],
        "assigned_to": ["user-xyz"],
        "properties": {"priority": "high"},
        "linked_entities": {},
        "history": [
            {
                "stage": "stage-new-lead",
                "entered_at": "2026-01-21T10:00:00Z",
                "exited_at": null
            }
        ],
        "tasks": [
            {
                "uid": "task-inst-123",
                "template_id": "task-initial-contact",
                "name": "Initial Contact",
                "status": "pending",
                "stage": "stage-new-lead",
                "field_values": []
            }
        ],
        "activities": [
            {
                "type": "CREATED",
                "subject": "Lead created",
                "performed_by": "user-xyz",
                "created_at": "2026-01-21T10:00:00Z"
            }
        ],
        "created_at": "2026-01-21T10:00:00Z",
        "updated_at": "2026-01-21T10:00:00Z",
        "created_by": "user-xyz"
    }
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    type: str = "lead"  # Document type discriminator
    uid: str  # Unique lead identifier (nanoid)
    item_id: str  # Human-readable ID (LEAD-202601-00001)
    current_stage: str  # Current stage UID
    status: WorkItemStatus = WorkItemStatus.PENDING
    name: str  # Lead name
    email: Optional[str] = None
    phone: Optional[str] = None
    config: str = "default"  # Config UID (always "default" for single workflow)
    config_values: List[ConfigFieldValue] = Field(default_factory=list)  # Custom field values
    assigned_to: List[str] = Field(default_factory=list)  # User IDs
    properties: Dict[str, Any] = Field(default_factory=dict)  # Generic metadata
    linked_entities: Dict[str, Any] = Field(default_factory=dict)  # Related entities
    history: List[HistoryData] = Field(default_factory=list)  # Stage transition timeline
    tasks: List[WorkItemTask] = Field(default_factory=list)  # Task instances
    activities: List[Activity] = Field(default_factory=list)  # Complete audit trail
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # User ID who created

    class Config:
        json_encoders = {ObjectId: str}


# ═══════════════════════════════════════════════════════════
# Configuration Model
# ═══════════════════════════════════════════════════════════

class WorkItemConfig(BaseModel):
    """
    Workflow configuration (single document).
    Stored in MongoDB with type="config", uid="default".
    Defines global custom fields for all leads.
    
    Example:
    {
        "_id": ObjectId("..."),
        "type": "config",
        "uid": "default",
        "workflow_name": "Lead Workflow",
        "is_active": true,
        "variables": [
            {
                "field_key": "budget",
                "label": "Budget",
                "field_type": "decimal",
                "input_type": "number",
                "required": true,
                "placeholder": "Enter budget amount",
                "validation_rules": {"min": 1000, "max": 1000000}
            },
            {
                "field_key": "lead_source",
                "label": "Lead Source",
                "field_type": "enum",
                "input_type": "dropdown",
                "options": ["Website", "Referral", "Cold Call", "Social Media"],
                "required": true
            },
            {
                "field_key": "company_size",
                "label": "Company Size",
                "field_type": "enum",
                "input_type": "dropdown",
                "options": ["1-10", "11-50", "51-200", "201-500", "500+"]
            }
        ],
        "created_at": "2026-01-21T00:00:00Z",
        "updated_at": "2026-01-21T00:00:00Z"
    }
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    type: str = "config"  # Document type discriminator
    uid: str = "default"  # Always "default" for single workflow
    workflow_name: str = "Lead Workflow"
    is_active: bool = True
    variables: List[FieldDefinition] = Field(default_factory=list)  # Global custom fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}


# ═══════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════

def generate_lead_id(prefix: str = "LEAD") -> str:
    """
    Generate unique lead ID in format: LEAD-YYYYMM-00001
    
    Args:
        prefix: Prefix for lead ID (default: "LEAD")
    
    Returns:
        Formatted lead ID string
    
    Example:
        >>> generate_lead_id()
        'LEAD-202601-00001'
    """
    from datetime import datetime
    current_date = datetime.now()
    return f"{prefix}-{current_date.strftime('%Y%m')}-00001"


def validate_field_value(field_def: FieldDefinition, value: Any) -> bool:
    """
    Validate a field value against its field definition.
    
    Args:
        field_def: FieldDefinition to validate against
        value: Value to validate
    
    Returns:
        True if valid, raises ValueError otherwise
    
    Example:
        >>> field_def = FieldDefinition(
        ...     field_key="budget",
        ...     field_type=FieldType.DECIMAL,
        ...     validation_rules={"min": 1000, "max": 1000000}
        ... )
        >>> validate_field_value(field_def, 50000)
        True
    """
    # Type validation
    if field_def.field_type == FieldType.INTEGER:
        if not isinstance(value, int):
            raise ValueError(f"{field_def.field_key}: Expected integer, got {type(value)}")
    elif field_def.field_type == FieldType.DECIMAL:
        if not isinstance(value, (int, float)):
            raise ValueError(f"{field_def.field_key}: Expected number, got {type(value)}")
    elif field_def.field_type == FieldType.BOOLEAN:
        if not isinstance(value, bool):
            raise ValueError(f"{field_def.field_key}: Expected boolean, got {type(value)}")
    
    # Custom validation rules
    if field_def.validation_rules:
        if "min" in field_def.validation_rules and value < field_def.validation_rules["min"]:
            raise ValueError(f"{field_def.field_key}: Value {value} below minimum {field_def.validation_rules['min']}")
        if "max" in field_def.validation_rules and value > field_def.validation_rules["max"]:
            raise ValueError(f"{field_def.field_key}: Value {value} exceeds maximum {field_def.validation_rules['max']}")
    
    # Required validation
    if field_def.required and value is None:
        raise ValueError(f"{field_def.field_key}: Required field cannot be None")
    
    return True


# ═══════════════════════════════════════════════════════════
# Export All Models
# ═══════════════════════════════════════════════════════════

__all__ = [
    # Enums
    "WorkItemTaskStatus",
    "WorkItemStatus",
    "FieldType",
    "ArrayItemType",
    "InputType",
    # Field Models
    "FieldDefinition",
    "FieldValueBase",
    "TaskFieldValue",
    "ConfigFieldValue",
    # Task Models
    "WorkStageTask",
    "WorkItemTask",
    # Stage Model
    "WorkStage",
    # Activity & History
    "Activity",
    "HistoryData",
    # Main Models
    "WorkItem",
    "WorkItemConfig",
    # Helpers
    "generate_lead_id",
    "validate_field_value",
]
