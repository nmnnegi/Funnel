# Lead CRM Standalone Project - Complete Reference

## 🎯 Project Overview

A fully customizable Lead CRM system with Kanban board built using:
- **Backend**: Django REST Framework (DRF)
- **Database**: MongoDB (ONLY - No PostgreSQL/Django models)
- **Data Models**: Pydantic Models (No Django ORM models)
- **Architecture**: Single collection design for maximum flexibility

## 🏗️ Architecture Philosophy

### Single Collection Design
Instead of multiple collections (leads, lead_stages, lead_configs), we consolidate everything under ONE collection called **`leads`** with a single workflow configuration.

**Why Single Collection?**
- User can create only 1 lead workflow (simplified UX)
- All stages, tasks, and lead data live in one place
- Easier to query and manage
- Reduces MongoDB complexity
- Perfect for a focused Lead CRM

### Data Structure
```
MongoDB Collection: leads
├── Lead Documents (type: "lead")
│   ├── lead_id (LEAD-202601-00001)
│   ├── name, email, phone
│   ├── current_stage (string - stage identifier)
│   ├── status (pending, in_progress, completed)
│   ├── config_values (custom fields)
│   ├── assigned_to (list of user IDs)
│   ├── tasks (embedded array of task instances)
│   ├── activities (embedded array of activity log)
│   └── history (embedded array of stage transitions)
│
├── Stage Documents (type: "stage")
│   ├── name, slug, color, description
│   ├── order (for Kanban board ordering)
│   ├── allowed_next_stages (workflow transitions)
│   └── stage_tasks (task templates for this stage)
│
└── Config Document (type: "config", single document)
    ├── workflow_name ("Lead Workflow")
    ├── variables (custom fields configuration)
    └── is_active (true)
```

## 🎨 Key Features

### 1. Kanban Board
- Drag-and-drop leads between stages
- Stage-based workflow management
- Visual pipeline representation
- Color-coded stages
- Task completion tracking per stage

### 2. Fully Customizable Fields
- Admin can define custom fields (FieldDefinition)
- Support multiple field types: string, number, date, boolean, enum, array, document
- Multiple input types: text, textarea, dropdown, date picker, file upload, etc.
- Field validation rules
- Default values and placeholders

### 3. Task Management
- Each stage can have required tasks
- Tasks act as gates before stage transitions
- Task variables for data collection
- Task completion tracking
- Task notes and attachments

### 4. Activity Timeline
- Complete audit trail of all changes
- Stage transitions
- Task completions
- Field updates
- Assignment changes
- Timestamps and user tracking

### 5. Lead Lifecycle
- Auto-generated Lead IDs (LEAD-202601-00001)
- Stage progression with history
- Status tracking (pending, in_progress, completed, blocked)
- Assignment management
- Custom properties and linked entities

## 📊 Pydantic Models (MongoDB Schema)

### Core Models

#### 1. **FieldDefinition** - Custom Field Configuration
```python
class FieldDefinition(BaseModel):
    field_key: str                    # Unique identifier
    label: str                        # Display name
    field_type: FieldType             # string, integer, decimal, boolean, date, datetime, enum, array, document
    input_type: InputType             # text, textarea, number, dropdown, date_picker, file_upload, etc.
    required: bool = False
    options: List[str] = []           # For enum/dropdown
    default_value: Optional[str] = None
    validation_rules: Dict[str, Any] = {}
    placeholder: str = ""
    help_text: str = ""
    order: int = 0
    is_active: bool = True
    array_item_type: Optional[ArrayItemType] = None  # For array fields
```

#### 2. **WorkStageTask** - Task Template
```python
class WorkStageTask(BaseModel):
    uid: str                          # Unique task ID
    name: str                         # Task name
    description: Optional[str] = None
    required: bool = False            # Must complete before stage transition
    order: int = 0
    is_active: bool = True
    task_variables: List[FieldDefinition] = []  # Fields to collect during task
```

#### 3. **WorkStage** - Stage Definition
```python
class WorkStage(BaseModel):
    _id: Optional[ObjectId]
    type: str = "stage"               # Document type discriminator
    uid: str                          # Unique stage ID
    name: str                         # "New Lead", "Contacted", "Qualified"
    slug: str                         # "new-lead", "contacted", "qualified"
    color: str = "#6B7280"            # Hex color for UI
    description: Optional[str] = None
    order: int = 0                    # Display order in Kanban
    is_active: bool = True
    allowed_next_stages: List[str] = []  # UIDs of stages can transition to
    stage_tasks: List[WorkStageTask] = []  # Required tasks for this stage
    created_at: datetime
    updated_at: datetime
```

#### 4. **TaskFieldValue** - Task Data Collection
```python
class TaskFieldValue(BaseModel):
    variable: str                     # field_key reference
    field_type: FieldType
    original_value: str = ""          # Source of truth
    value: Any = None                 # Parsed/typed value
```

#### 5. **WorkItemTask** - Task Instance
```python
class WorkItemTask(BaseModel):
    uid: str                          # Unique task instance ID
    name: str
    description: Optional[str] = None
    template_id: str                  # Reference to WorkStageTask.uid
    stage: str                        # Stage UID where task was created
    status: WorkItemTaskStatus        # pending, in_progress, completed, skipped, blocked
    required: bool = False
    order: int = 0
    is_active: bool = True
    task_variables: List[FieldDefinition] = []
    completed_at: Optional[datetime] = None
    completed_by: Optional[str] = None  # User ID
    notes: str = ""
    field_values: List[TaskFieldValue] = []
```

#### 6. **Activity** - Audit Log Entry
```python
class Activity(BaseModel):
    type: str                         # STAGE_CHANGE, TASK_COMPLETED, FIELD_UPDATED, CREATED, ASSIGNED
    subject: str                      # Human-readable summary
    description: Optional[str] = None
    performed_by: Optional[str] = None  # User ID
    created_at: datetime
    created_by: Optional[str] = None    # User ID
    activity_data: Dict[str, Any] = {}  # Additional metadata
```

#### 7. **HistoryData** - Stage Transition History
```python
class HistoryData(BaseModel):
    stage: str                        # Stage UID
    entered_at: datetime
    exited_at: Optional[datetime] = None
```

#### 8. **ConfigFieldValue** - Lead Custom Field Value
```python
class ConfigFieldValue(BaseModel):
    variable: str                     # field_key reference
    field_type: FieldType
    original_value: str = ""
    value: Any = None
```

#### 9. **WorkItem (Lead)** - Main Lead Document
```python
class WorkItem(BaseModel):
    _id: Optional[ObjectId]
    type: str = "lead"                # Document type discriminator
    uid: str                          # Unique lead ID
    item_id: str                      # LEAD-202601-00001
    current_stage: str                # Stage UID
    status: WorkItemStatus            # pending, in_progress, completed, skipped, blocked
    name: str                         # Lead name
    email: Optional[str] = None
    phone: Optional[str] = None
    config: str = "default"           # Config UID (always "default" for single workflow)
    config_values: List[ConfigFieldValue] = []  # Custom field values
    assigned_to: List[str] = []       # User IDs
    properties: Dict[str, Any] = {}   # Generic metadata
    linked_entities: Dict[str, Any] = {}  # Related records
    history: List[HistoryData] = []   # Stage transition timeline
    tasks: List[WorkItemTask] = []    # Task instances
    activities: List[Activity] = []   # Complete audit trail
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None  # User ID
```

#### 10. **WorkItemConfig** - Workflow Configuration (Single Document)
```python
class WorkItemConfig(BaseModel):
    _id: Optional[ObjectId]
    type: str = "config"              # Document type discriminator
    uid: str = "default"              # Always "default" for single workflow
    workflow_name: str = "Lead Workflow"
    is_active: bool = True
    variables: List[FieldDefinition] = []  # Global lead custom fields
    created_at: datetime
    updated_at: datetime
```

## 🔄 Core Operations

### 1. **Create Lead**
```python
# Steps:
1. Get or create config (always uid="default")
2. Validate custom field values
3. Get current stage
4. Generate lead_id (LEAD-202601-00001)
5. Create tasks from stage template
6. Create lead document in MongoDB
7. Add creation activity
8. Add initial history entry

# MongoDB Document:
{
    "type": "lead",
    "uid": "uid-abc123",
    "item_id": "LEAD-202601-00001",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "current_stage": "stage-new-lead",
    "status": "pending",
    "config": "default",
    "config_values": [
        {"variable": "budget", "field_type": "decimal", "original_value": "50000", "value": 50000.0}
    ],
    "assigned_to": ["user-xyz"],
    "tasks": [
        {
            "uid": "task-123",
            "template_id": "task-template-1",
            "stage": "stage-new-lead",
            "name": "Initial Contact",
            "status": "pending",
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
    "history": [
        {
            "stage": "stage-new-lead",
            "entered_at": "2026-01-21T10:00:00Z"
        }
    ]
}
```

### 2. **Stage Transition**
```python
# Steps:
1. Validate current stage allows transition to target stage
2. Check all required tasks are completed
3. Exit current stage in history
4. Create tasks from new stage template
5. Update current_stage
6. Add history entry for new stage
7. Add stage change activity

# Activity Log:
{
    "type": "STAGE_CHANGE",
    "subject": "Lead moved to Contacted",
    "activity_data": {
        "from_stage": "New Lead",
        "to_stage": "Contacted",
        "comment": "Successfully reached out via email"
    }
}
```

### 3. **Complete Task**
```python
# Steps:
1. Find task by uid in lead.tasks array
2. Validate all required task variables are filled
3. Update task status to "completed"
4. Set completed_at, completed_by
5. Store field_values
6. Add task completion activity

# Task Completion:
{
    "uid": "task-123",
    "status": "completed",
    "completed_at": "2026-01-21T11:00:00Z",
    "completed_by": "user-xyz",
    "notes": "Contact established successfully",
    "field_values": [
        {"variable": "contact_method", "field_type": "enum", "original_value": "email", "value": "email"}
    ]
}
```

### 4. **Update Custom Fields**
```python
# Steps:
1. Validate field definitions from config
2. Type check and convert values
3. Update config_values array
4. Add field update activity

# Field Update Activity:
{
    "type": "FIELD_UPDATED",
    "subject": "Budget updated",
    "activity_data": {
        "field": "budget",
        "old_value": "50000",
        "new_value": "75000"
    }
}
```

### 5. **Kanban Board Query**
```python
# Group leads by stage
pipeline = [
    {"$match": {"type": "lead"}},
    {"$group": {
        "_id": "$current_stage",
        "leads": {"$push": "$$ROOT"},
        "count": {"$sum": 1}
    }},
    {"$lookup": {
        "from": "leads",
        "let": {"stage_uid": "$_id"},
        "pipeline": [
            {"$match": {
                "$expr": {"$and": [
                    {"$eq": ["$type", "stage"]},
                    {"$eq": ["$uid", "$$stage_uid"]}
                ]}
            }}
        ],
        "as": "stage_info"
    }},
    {"$sort": {"stage_info.order": 1}}
]

# Result:
[
    {
        "stage": {"name": "New Lead", "color": "#3B82F6", "order": 0},
        "leads": [...],
        "count": 5
    },
    {
        "stage": {"name": "Contacted", "color": "#10B981", "order": 1},
        "leads": [...],
        "count": 3
    }
]
```

## 🛠️ Technical Implementation

### MongoDB Connection
```python
# No Django models, direct MongoDB connection
from pymongo import MongoClient
from pymongo.asynchronous.client import AsyncMongoClient

# Sync client
mongo_client = MongoClient("mongodb://localhost:27017")
leads_collection = mongo_client.lead_crm.leads

# Async client
async_mongo_client = AsyncMongoClient("mongodb://localhost:27017")
async_leads_collection = async_mongo_client.lead_crm.leads
```

### Service Layer
```python
class LeadService:
    """MongoDB operations with Pydantic validation"""
    
    def __init__(self, collection):
        self.collection = collection
    
    def create_lead(self, lead_data: dict) -> str:
        """Validate with Pydantic, insert to MongoDB"""
        lead = WorkItem(**lead_data)
        result = self.collection.insert_one(
            lead.model_dump(mode="json", exclude_none=True)
        )
        return str(result.inserted_id)
    
    def get_lead(self, uid: str) -> Optional[WorkItem]:
        """Fetch and validate with Pydantic"""
        doc = self.collection.find_one({"type": "lead", "uid": uid})
        return WorkItem(**doc) if doc else None
    
    def transition_stage(self, uid: str, new_stage: str, comment: str = ""):
        """Handle stage transition with validation"""
        # Implementation...
```

### DRF ViewSet (No Django ORM)
```python
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

class LeadViewSet(ViewSet):
    """Lead CRUD operations using MongoDB directly"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lead_service = LeadService(leads_collection)
    
    def list(self, request):
        """List all leads"""
        # Query MongoDB directly
        # Paginate
        # Return serialized response
    
    def create(self, request):
        """Create new lead"""
        serializer = LeadCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Create in MongoDB
    
    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        """Transition lead to new stage"""
        # Validate and update MongoDB
```

### Serializers (Request/Response)
```python
class LeadCreateSerializer(serializers.Serializer):
    """For creating leads"""
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=20, required=False)
    stage = serializers.CharField()  # Stage UID
    config_values = serializers.ListField(child=FieldValueSerializer())
    assigned_to = serializers.ListField(child=serializers.CharField())

class LeadResponseSerializer(serializers.Serializer):
    """For returning lead data"""
    uid = serializers.CharField()
    item_id = serializers.CharField()
    name = serializers.CharField()
    email = serializers.CharField()
    current_stage = WorkflowStageSerializer()
    status = serializers.CharField()
    config_values = serializers.ListField(child=FieldValueSerializer())
    tasks = serializers.ListField(child=WorkItemTaskSerializer())
    activities = serializers.ListField(child=ActivitySerializer())
    history = serializers.ListField(child=HistoryDataSerializer())
```

## 📱 API Endpoints

### Lead Management
```
POST   /api/leads/                    # Create lead
GET    /api/leads/                    # List leads (with filters)
GET    /api/leads/{uid}/              # Get lead details
PATCH  /api/leads/{uid}/              # Update lead fields
DELETE /api/leads/{uid}/              # Delete lead (soft)

POST   /api/leads/{uid}/transition/   # Transition to new stage
POST   /api/leads/{uid}/assign/       # Assign to users
```

### Task Management
```
GET    /api/leads/{uid}/tasks/        # List lead tasks
POST   /api/leads/{uid}/tasks/{task_uid}/complete/  # Complete task
```

### Activity Log
```
GET    /api/leads/{uid}/activities/   # Get activity timeline
POST   /api/leads/{uid}/activities/   # Add manual activity
```

### Stage Management
```
POST   /api/stages/                   # Create stage
GET    /api/stages/                   # List all stages
GET    /api/stages/{uid}/             # Get stage details
PATCH  /api/stages/{uid}/             # Update stage
DELETE /api/stages/{uid}/             # Delete stage
POST   /api/stages/reorder/           # Reorder stages
```

### Configuration
```
GET    /api/config/                   # Get workflow config (single)
PATCH  /api/config/                   # Update config variables
```

### Kanban Board
```
GET    /api/kanban/                   # Get Kanban board data (grouped by stage)
POST   /api/kanban/move/              # Move lead between stages
```

## 🎨 Kanban Board Implementation

### Data Structure for UI
```json
{
  "stages": [
    {
      "uid": "stage-new",
      "name": "New Lead",
      "color": "#3B82F6",
      "order": 0,
      "lead_count": 5,
      "leads": [
        {
          "uid": "lead-123",
          "item_id": "LEAD-202601-00001",
          "name": "John Doe",
          "email": "john@example.com",
          "assigned_to": ["user-xyz"],
          "status": "pending",
          "pending_tasks": 2,
          "created_at": "2026-01-21T10:00:00Z"
        }
      ]
    },
    {
      "uid": "stage-contacted",
      "name": "Contacted",
      "color": "#10B981",
      "order": 1,
      "lead_count": 3,
      "leads": [...]
    }
  ]
}
```

### Drag & Drop Logic
```python
@action(detail=False, methods=['post'], url_path='kanban/move')
def kanban_move(self, request):
    """
    Move lead between stages via drag & drop
    
    Request:
    {
        "lead_uid": "lead-123",
        "from_stage": "stage-new",
        "to_stage": "stage-contacted",
        "position": 2  # Optional: for ordering within stage
    }
    """
    # 1. Validate stage transition allowed
    # 2. Check required tasks completed
    # 3. Perform stage transition
    # 4. Return updated Kanban data
```

## 📊 Sample Data Setup

### Initial Config Document
```json
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
            "placeholder": "Enter budget amount"
        },
        {
            "field_key": "source",
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
```

### Sample Stages
```json
[
    {
        "type": "stage",
        "uid": "stage-new",
        "name": "New Lead",
        "slug": "new-lead",
        "color": "#3B82F6",
        "order": 0,
        "allowed_next_stages": ["stage-contacted"],
        "stage_tasks": [
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
        ]
    },
    {
        "type": "stage",
        "uid": "stage-contacted",
        "name": "Contacted",
        "slug": "contacted",
        "color": "#10B981",
        "order": 1,
        "allowed_next_stages": ["stage-qualified", "stage-lost"],
        "stage_tasks": [
            {
                "uid": "task-qualify",
                "name": "Qualification Call",
                "description": "Qualify the lead based on criteria",
                "required": true,
                "task_variables": [
                    {
                        "field_key": "qualification_score",
                        "label": "Qualification Score",
                        "field_type": "integer",
                        "input_type": "number",
                        "validation_rules": {"min": 0, "max": 10}
                    }
                ]
            }
        ]
    },
    {
        "type": "stage",
        "uid": "stage-qualified",
        "name": "Qualified",
        "slug": "qualified",
        "color": "#F59E0B",
        "order": 2,
        "allowed_next_stages": ["stage-proposal", "stage-lost"],
        "stage_tasks": []
    },
    {
        "type": "stage",
        "uid": "stage-proposal",
        "name": "Proposal Sent",
        "slug": "proposal",
        "color": "#8B5CF6",
        "order": 3,
        "allowed_next_stages": ["stage-won", "stage-lost"],
        "stage_tasks": []
    },
    {
        "type": "stage",
        "uid": "stage-won",
        "name": "Won",
        "slug": "won",
        "color": "#059669",
        "order": 4,
        "allowed_next_stages": [],
        "stage_tasks": []
    },
    {
        "type": "stage",
        "uid": "stage-lost",
        "name": "Lost",
        "slug": "lost",
        "color": "#DC2626",
        "order": 5,
        "allowed_next_stages": [],
        "stage_tasks": []
    }
]
```

## 🚀 Next Steps

1. **Set up Django project with DRF**
2. **Install MongoDB driver** (pymongo, motor for async)
3. **Implement Pydantic models** (from models.py reference)
4. **Create LeadService** (MongoDB operations)
5. **Build DRF ViewSets** (no Django ORM)
6. **Implement serializers** (request/response)
7. **Add Kanban board endpoint**
8. **Build frontend** (React/Vue with drag-drop)

## 📚 Dependencies

```
Django>=4.2
djangorestframework>=3.14
pymongo>=4.6
motor>=3.3  # For async operations
pydantic>=2.0
drf-yasg>=1.21  # For Swagger/OpenAPI
```

---

**This reference provides everything needed to build a standalone Lead CRM with MongoDB as the only database, using Pydantic models and DRF!**
