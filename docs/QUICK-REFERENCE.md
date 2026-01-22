# 🎯 Lead CRM Standalone - Quick Reference Card

## 📦 What You Have

### File Structure
```
lead-crm-standalone-reference/
├── README.md                      # Start here! Complete guide + quick start
├── PROJECT-OVERVIEW.md            # Full architecture & design documentation (23KB)
├── PYDANTIC-MODELS.py            # Production-ready Pydantic models (22KB)
└── SERVICE-IMPLEMENTATION.py      # Complete MongoDB service layer (26KB)
```

## 🚀 Quick Start (5 Minutes)

### 1. Copy Files to Your Project
```bash
# Create new Django project
django-admin startproject lead_crm
cd lead_crm
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install Django djangorestframework pymongo pydantic drf-yasg

# Copy reference files
mkdir leads
cp ../lead-crm-standalone-reference/PYDANTIC-MODELS.py leads/models.py
cp ../lead-crm-standalone-reference/SERVICE-IMPLEMENTATION.py leads/services.py
```

### 2. Configure MongoDB
```python
# settings.py
INSTALLED_APPS = [
    'rest_framework',
    'drf_yasg',
    'leads',
]

MONGODB_CONFIG = {
    'host': 'localhost',
    'port': 27017,
    'database': 'lead_crm',
}
```

### 3. Initialize Database
```python
# Run in Django shell
from pymongo import MongoClient
from leads.models import WorkStage, WorkItemConfig, FieldDefinition, FieldType, InputType

client = MongoClient('mongodb://localhost:27017')
db = client.lead_crm
leads_collection = db.leads

# Create config
config = WorkItemConfig(
    uid="default",
    workflow_name="Lead Workflow",
    variables=[
        FieldDefinition(
            field_key="budget",
            label="Budget",
            field_type=FieldType.DECIMAL,
            input_type=InputType.NUMBER,
            required=True
        )
    ]
)
leads_collection.insert_one(config.model_dump(mode="json"))

# Create stages
stages = [
    WorkStage(uid="stage-new", name="New Lead", slug="new-lead", color="#3B82F6", order=0),
    WorkStage(uid="stage-contacted", name="Contacted", slug="contacted", color="#10B981", order=1),
    WorkStage(uid="stage-qualified", name="Qualified", slug="qualified", color="#F59E0B", order=2),
    WorkStage(uid="stage-won", name="Won", slug="won", color="#059669", order=3),
]
for stage in stages:
    leads_collection.insert_one(stage.model_dump(mode="json"))
```

### 4. Done! Start Building
You now have:
- ✅ Complete Pydantic models
- ✅ Full service layer (CRUD + business logic)
- ✅ MongoDB initialized with stages
- ✅ Ready to build ViewSets and API

## 📊 Key Design Decisions

### Single Collection Strategy
```
MongoDB: lead_crm.leads
├── Documents with type="lead"     (all leads)
├── Documents with type="stage"    (pipeline stages)
└── Document with type="config"    (single workflow config, uid="default")
```

**Why?** Simplified queries, single workflow, easier management.

### No Django ORM Models
- ❌ No Django models for PostgreSQL
- ✅ Direct MongoDB with PyMongo
- ✅ Pydantic for validation
- ✅ DRF ViewSets without ORM

### Embedded Documents
```python
Lead Document {
    "tasks": [...],        # Embedded
    "activities": [...],   # Embedded
    "history": [...]       # Embedded
}
```

**Why?** Single query for complete data, no joins, better performance.

## 🎨 Core Features Included

### 1. Full Lead Lifecycle
- Auto-generated Lead IDs (LEAD-202601-00001)
- Custom fields (budget, source, company size, etc.)
- Stage-based workflow
- Assignment to users
- Properties and linked entities

### 2. Kanban Board Ready
- Group leads by stage
- Drag & drop between stages
- Color-coded stages
- Task completion tracking
- Lead counts per stage

### 3. Task Management
- Task templates in stages
- Task instances in leads
- Required tasks block transitions
- Task variables for data collection
- Task completion with notes

### 4. Complete Audit Trail
- All changes logged in activities
- Stage transition history
- Task completions
- Field updates
- Assignment changes

### 5. Flexible Custom Fields
- Define any field type (string, number, date, enum, array, document)
- Multiple input types (text, dropdown, date picker, file upload)
- Validation rules
- Required/optional fields
- Help text and placeholders

## 📚 What Each File Contains

### PROJECT-OVERVIEW.md (23KB)
- Complete architecture explanation
- All Pydantic models with examples
- MongoDB document structure
- API endpoints specification
- Kanban board implementation
- Sample data setup
- Core operations flow

### PYDANTIC-MODELS.py (22KB)
- Production-ready models
- All enums (WorkItemStatus, FieldType, InputType, etc.)
- Field definitions and values
- Task models (templates + instances)
- Activity and history tracking
- Helper functions
- Complete docstrings and examples

### SERVICE-IMPLEMENTATION.py (26KB)
- Complete LeadService class
- All CRUD operations (create, read, update, delete)
- Stage transitions with validation
- Task completion
- Kanban board data
- Activity logging
- Stage management
- Config management
- Both sync and async methods

### README.md (14KB)
- Quick start guide
- Setup instructions
- Implementation examples
- Frontend integration (React Kanban)
- MongoDB indexes
- API endpoints summary
- Best practices

## 🔑 Most Important Methods

### LeadService
```python
# Create lead
mongo_id = lead_service.create_lead(lead_data)

# List leads with pagination
leads, total = lead_service.list_leads(filters={...}, limit=10, offset=0)

# Get single lead
lead = lead_service.get_lead(uid)

# Transition stage
lead_service.transition_stage(lead_uid, new_stage_uid, comment, performed_by)

# Complete task
lead_service.complete_task(lead_uid, task_uid, field_values, notes, completed_by)

# Get Kanban data
kanban_data = lead_service.get_kanban_data()

# Generate unique lead ID
lead_id = lead_service.generate_lead_id()  # LEAD-202601-00001
```

## 📱 API Endpoints to Build

```
POST   /api/leads/                    # Create lead
GET    /api/leads/                    # List leads
GET    /api/leads/{uid}/              # Get lead
PATCH  /api/leads/{uid}/              # Update lead
DELETE /api/leads/{uid}/              # Delete lead

POST   /api/leads/{uid}/transition/   # Transition stage
POST   /api/leads/{uid}/assign/       # Assign users
GET    /api/leads/{uid}/tasks/        # List tasks
POST   /api/leads/{uid}/tasks/{task_uid}/complete/  # Complete task

GET    /api/leads/kanban/             # Kanban board data
POST   /api/leads/kanban/move/        # Drag & drop

POST   /api/stages/                   # Create stage
GET    /api/stages/                   # List stages
GET    /api/stages/{uid}/             # Get stage
PATCH  /api/stages/{uid}/             # Update stage
POST   /api/stages/reorder/           # Reorder stages

GET    /api/config/                   # Get config
PATCH  /api/config/                   # Update config
```

## 🎓 Next Steps

1. **Copy files** to your Django project
2. **Configure MongoDB** connection
3. **Initialize** sample stages and config
4. **Build ViewSets** using the service layer
5. **Create serializers** for request/response
6. **Build frontend** with Kanban board
7. **Add authentication** (if needed)
8. **Deploy** and enjoy!

## 💡 Pro Tips

1. **Always validate with Pydantic** before MongoDB operations
2. **Use transactions** for multi-step operations
3. **Index frequently queried fields** (type, uid, current_stage)
4. **Paginate list endpoints** to avoid performance issues
5. **Validate stage transitions** before allowing moves
6. **Log all activities** for complete audit trail
7. **Check required tasks** before stage transitions
8. **Use field definitions** for dynamic form generation

## 📞 Common Questions

**Q: Can I have multiple workflows?**
A: Current design is single workflow (uid="default"). To support multiple, change config to allow multiple docs and add workflow_uid to leads.

**Q: How do I add custom fields?**
A: Update config.variables via PATCH /api/config/ endpoint. Each FieldDefinition defines a custom field.

**Q: Can tasks have subtasks?**
A: Not in current design. Extend WorkItemTask to include subtasks array if needed.

**Q: How to handle file uploads?**
A: Use FieldType.DOCUMENT with InputType.FILE_UPLOAD. Store S3 URLs in field values.

**Q: Can I customize activity types?**
A: Yes! Activity.type is a string. Use any type like "EMAIL_SENT", "CALL_MADE", "MEETING_SCHEDULED".

## 🎯 Summary

You have **everything needed** to build a production-ready Lead CRM:
- ✅ Complete data models (Pydantic)
- ✅ Full service layer (business logic)
- ✅ Clear architecture (single collection)
- ✅ Implementation examples
- ✅ API specifications
- ✅ Kanban board design
- ✅ Sample data

**Total: 85KB of production-ready code and documentation!**

---

**Start with README.md and follow the quick start guide. You'll have a working Lead CRM in under 30 minutes!** 🚀
