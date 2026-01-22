from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum


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


class FieldDefinition(BaseModel):
    """Reusable field definition for custom fields."""

    field_key: str
    label: str
    field_type: FieldType
    input_type: InputType
    required: bool = False
    options: List[str] = Field(default_factory=list)
    default_value: Optional[str] = None
    validation_rules: Dict[str, Any] = Field(default_factory=dict)
    placeholder: str = ""
    help_text: str = ""
    order: int = 0
    is_active: bool = True
    array_item_type: Optional[ArrayItemType] = None

    class Config:
        populate_by_name = True


class FieldValueBase(BaseModel):
    """Base model for storing field values"""

    variable: str
    field_type: FieldType
    original_value: str = ""
    value: Any = None

    class Config:
        populate_by_name = True


class TaskFieldValue(FieldValueBase):
    """Field value for task variables"""

    pass


class ConfigFieldValue(FieldValueBase):
    """Field value for lead config variables"""

    pass


class WorkStageTask(BaseModel):
    """Task template attached to a stage"""

    uid: str
    name: str
    description: Optional[str] = None
    required: bool = False
    order: int = 0
    is_active: bool = True
    task_variables: List[FieldDefinition] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class WorkItemTask(BaseModel):
    """Task instance created when a lead enters a stage"""

    uid: str
    name: str
    description: Optional[str] = None
    template_id: str
    stage: str
    status: WorkItemTaskStatus = WorkItemTaskStatus.PENDING
    required: bool = False
    order: int = 0
    is_active: bool = True
    task_variables: List[FieldDefinition] = Field(default_factory=list)
    completed_at: Optional[datetime] = None
    completed_by: Optional[str] = None
    notes: str = ""
    field_values: List[TaskFieldValue] = Field(default_factory=list)

    class Config:
        json_encoders = {ObjectId: str}


class WorkStage(BaseModel):
    """Stage definition in the workflow pipeline"""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    uid: str
    config: str  # Config UID this stage belongs to
    name: str
    slug: str
    color: str = "#6B7280"
    description: Optional[str] = None
    order: int = 0
    is_active: bool = True
    allowed_next_stages: List[str] = Field(default_factory=list)
    stage_tasks: List[WorkStageTask] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Activity(BaseModel):
    """Activity log entry for audit trail"""

    type: str
    subject: str
    description: Optional[str] = None
    performed_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    activity_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {ObjectId: str}


class HistoryData(BaseModel):
    """Stage transition history entry"""

    stage: str
    entered_at: datetime = Field(default_factory=datetime.utcnow)
    exited_at: Optional[datetime] = None

    class Config:
        json_encoders = {ObjectId: str}


class WorkItem(BaseModel):
    """Main Lead document (WorkItem)"""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    uid: str
    item_id: str
    current_stage: str
    status: WorkItemStatus = WorkItemStatus.PENDING
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    config: str  # Config UID this lead belongs to
    config_values: List[ConfigFieldValue] = Field(default_factory=list)
    assigned_to: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    linked_entities: Dict[str, Any] = Field(default_factory=dict)
    history: List[HistoryData] = Field(default_factory=list)
    tasks: List[WorkItemTask] = Field(default_factory=list)
    activities: List[Activity] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None

    class Config:
        json_encoders = {ObjectId: str}


class WorkItemConfig(BaseModel):
    """Workflow configuration (supports multiple workflows)"""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    uid: str  # Unique identifier for this workflow
    workflow_name: str  # Name of the workflow
    is_active: bool = True
    variables: List[FieldDefinition] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}


def generate_lead_id(collection, prefix: str = "LEAD") -> str:
    """
    Generate unique lead ID in format: LEAD-YYYYMM-00001
    """
    from datetime import datetime

    current_date = datetime.now()
    year_month = current_date.strftime("%Y%m")

    # Find the highest number for this month
    prefix_pattern = f"{prefix}-{year_month}-"
    last_lead = collection.find_one(
        {"item_id": {"$regex": f"^{prefix_pattern}"}}, sort=[("item_id", -1)]
    )

    if last_lead and "item_id" in last_lead:
        last_num = int(last_lead["item_id"].split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1

    return f"{prefix}-{year_month}-{new_num:05d}"


def validate_field_value(field_def: FieldDefinition, value: Any) -> bool:
    """Validate a field value against its field definition"""
    if field_def.field_type == FieldType.INTEGER:
        if not isinstance(value, int):
            raise ValueError(
                f"{field_def.field_key}: Expected integer, got {type(value)}"
            )
    elif field_def.field_type == FieldType.DECIMAL:
        if not isinstance(value, (int, float)):
            raise ValueError(
                f"{field_def.field_key}: Expected number, got {type(value)}"
            )
    elif field_def.field_type == FieldType.BOOLEAN:
        if not isinstance(value, bool):
            raise ValueError(
                f"{field_def.field_key}: Expected boolean, got {type(value)}"
            )

    if field_def.validation_rules:
        if (
            "min" in field_def.validation_rules
            and value < field_def.validation_rules["min"]
        ):
            raise ValueError(
                f"{field_def.field_key}: Value {value} below minimum {field_def.validation_rules['min']}"
            )
        if (
            "max" in field_def.validation_rules
            and value > field_def.validation_rules["max"]
        ):
            raise ValueError(
                f"{field_def.field_key}: Value {value} exceeds maximum {field_def.validation_rules['max']}"
            )

    if field_def.required and value is None:
        raise ValueError(f"{field_def.field_key}: Required field cannot be None")

    return True
