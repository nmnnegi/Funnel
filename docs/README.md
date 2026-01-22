# Lead CRM Standalone - Complete Reference Package

## 📁 What's Inside

This reference package contains everything you need to build a standalone Lead CRM system with Django DRF and MongoDB (no PostgreSQL/Django models).

### Files

1. **PROJECT-OVERVIEW.md** - Complete project documentation with:
   - Architecture philosophy
   - Single collection design
   - All Pydantic models with examples
   - API endpoints specification
   - Kanban board implementation
   - Sample data setup
   - Technical implementation details

2. **PYDANTIC-MODELS.py** - Production-ready Pydantic models:
   - All enums (WorkItemStatus, FieldType, InputType, etc.)
   - FieldDefinition for custom fields
   - WorkStage for pipeline stages
   - WorkItem (Lead) with full lifecycle
   - WorkItemConfig for workflow configuration
   - Task models (templates and instances)
   - Activity and History tracking
   - Helper functions for validation

## 🎯 Key Decisions Made

### 1. Single Collection Design
Instead of separate collections for leads, stages, and configs, everything lives in ONE MongoDB collection: `leads`

**Document Types in `leads` collection:**
- `type="lead"` - Lead documents with all data
- `type="stage"` - Stage configuration documents
- `type="config"` - Single workflow configuration (uid="default")

**Why?**
- User creates only 1 workflow (simplified)
- Easier queries and aggregations
- Single source of truth
- Reduced MongoDB complexity
- Perfect for focused Lead CRM

### 2. No Django ORM Models
- **Zero Django models** for PostgreSQL
- Direct MongoDB operations via PyMongo/Motor
- Pydantic models for validation and type safety
- DRF ViewSets without Django ORM

### 3. Embedded Documents Pattern
Instead of references, we embed related data:
- Tasks embedded in leads
- Activities embedded in leads
- History embedded in leads
- Task templates embedded in stages

**Benefits:**
- Single query to get complete lead data
- No joins required
- Better read performance
- Atomic updates

## 🚀 Quick Start Guide

### Step 1: Set Up Django Project
```bash
django-admin startproject lead_crm
cd lead_crm
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install Django djangorestframework pymongo motor pydantic drf-yasg
```

### Step 2: Configure MongoDB
```python
# settings.py
MONGODB_CONFIG = {
    'host': 'localhost',
    'port': 27017,
    'database': 'lead_crm',
    'collection': 'leads'
}

# database.py
from pymongo import MongoClient
from pymongo.asynchronous.client import AsyncMongoClient

mongo_client = MongoClient(
    host=MONGODB_CONFIG['host'],
    port=MONGODB_CONFIG['port']
)
database = mongo_client[MONGODB_CONFIG['database']]
leads_collection = database[MONGODB_CONFIG['collection']]

# Async
async_mongo_client = AsyncMongoClient(
    host=MONGODB_CONFIG['host'],
    port=MONGODB_CONFIG['port']
)
async_database = async_mongo_client[MONGODB_CONFIG['database']]
async_leads_collection = async_database[MONGODB_CONFIG['collection']]
```

### Step 3: Copy Pydantic Models
Copy `PYDANTIC-MODELS.py` to your project:
```bash
cp PYDANTIC-MODELS.py lead_crm/leads/models.py
```

### Step 4: Create Service Layer
```python
# leads/services.py
from pymongo.collection import Collection
from typing import Optional, List, Dict, Any
from .models import WorkItem, WorkStage, WorkItemConfig

class LeadService:
    def __init__(self, collection: Collection):
        self.collection = collection
    
    def create_lead(self, lead_data: dict) -> str:
        """Create lead with Pydantic validation"""
        lead = WorkItem(**lead_data)
        result = self.collection.insert_one(
            lead.model_dump(mode="json", exclude_none=True)
        )
        return str(result.inserted_id)
    
    def get_lead(self, uid: str) -> Optional[WorkItem]:
        """Get lead by uid"""
        doc = self.collection.find_one({"type": "lead", "uid": uid})
        return WorkItem(**doc) if doc else None
    
    def list_leads(self, filters: dict = None, limit: int = 10, offset: int = 0) -> List[WorkItem]:
        """List leads with pagination"""
        query = {"type": "lead"}
        if filters:
            query.update(filters)
        
        cursor = self.collection.find(query).skip(offset).limit(limit)
        return [WorkItem(**doc) for doc in cursor]
    
    def get_kanban_data(self) -> List[Dict]:
        """Get Kanban board data grouped by stage"""
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
            {"$unwind": "$stage_info"},
            {"$sort": {"stage_info.order": 1}}
        ]
        return list(self.collection.aggregate(pipeline))
```

### Step 5: Create DRF ViewSets
```python
# leads/views.py
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .services import LeadService
from .serializers import (
    LeadCreateSerializer,
    LeadResponseSerializer,
    LeadListResponseSerializer
)

class LeadViewSet(ViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lead_service = LeadService(leads_collection)
    
    def list(self, request):
        """List all leads"""
        limit = int(request.query_params.get('limit', 10))
        offset = int(request.query_params.get('offset', 0))
        
        leads = self.lead_service.list_leads(limit=limit, offset=offset)
        serializer = LeadListResponseSerializer({
            'results': leads,
            'next': None,
            'previous': None
        })
        return Response(serializer.data)
    
    def create(self, request):
        """Create new lead"""
        serializer = LeadCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create lead in MongoDB
        lead_id = self.lead_service.create_lead(serializer.validated_data)
        
        # Fetch and return
        lead = self.lead_service.get_lead(serializer.validated_data['uid'])
        response_serializer = LeadResponseSerializer(lead)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='kanban')
    def kanban(self, request):
        """Get Kanban board data"""
        data = self.lead_service.get_kanban_data()
        return Response(data)
    
    @action(detail=True, methods=['post'], url_path='transition')
    def transition(self, request, pk=None):
        """Transition lead to new stage"""
        # Implementation
        pass
```

### Step 6: Initialize Sample Data
```python
# management/commands/init_lead_data.py
from django.core.management.base import BaseCommand
from leads.models import WorkStage, WorkItemConfig
from datetime import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
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
                ),
                # ... more fields
            ]
        )
        
        # Create stages
        stages = [
            WorkStage(
                uid="stage-new",
                name="New Lead",
                slug="new-lead",
                color="#3B82F6",
                order=0,
                allowed_next_stages=["stage-contacted"]
            ),
            # ... more stages
        ]
        
        # Insert to MongoDB
        leads_collection.insert_one(config.model_dump(mode="json"))
        for stage in stages:
            leads_collection.insert_one(stage.model_dump(mode="json"))
```

## 🎨 Frontend Integration

### Kanban Board Component (React Example)
```jsx
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

function KanbanBoard() {
  const [stages, setStages] = useState([]);
  
  useEffect(() => {
    fetch('/api/leads/kanban/')
      .then(res => res.json())
      .then(data => setStages(data));
  }, []);
  
  const onDragEnd = (result) => {
    // Handle drag & drop
    const { source, destination, draggableId } = result;
    
    fetch(`/api/leads/${draggableId}/transition/`, {
      method: 'POST',
      body: JSON.stringify({
        to_stage: destination.droppableId
      })
    });
  };
  
  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div className="kanban-board">
        {stages.map(stage => (
          <Droppable key={stage.uid} droppableId={stage.uid}>
            {(provided) => (
              <div
                ref={provided.innerRef}
                className="kanban-column"
                style={{ borderTopColor: stage.color }}
              >
                <h3>{stage.name} ({stage.count})</h3>
                {stage.leads.map((lead, index) => (
                  <Draggable key={lead.uid} draggableId={lead.uid} index={index}>
                    {(provided) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        className="kanban-card"
                      >
                        <h4>{lead.name}</h4>
                        <p>{lead.email}</p>
                        <span>Tasks: {lead.tasks.filter(t => t.status === 'completed').length}/{lead.tasks.length}</span>
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        ))}
      </div>
    </DragDropContext>
  );
}
```

## 📊 MongoDB Indexes

Create these indexes for better performance:

```javascript
// In MongoDB shell
use lead_crm

// Compound index for type and uid
db.leads.createIndex({ "type": 1, "uid": 1 })

// Index for lead queries
db.leads.createIndex({ "type": 1, "current_stage": 1 })
db.leads.createIndex({ "type": 1, "status": 1 })
db.leads.createIndex({ "type": 1, "created_at": -1 })
db.leads.createIndex({ "type": 1, "email": 1 })
db.leads.createIndex({ "type": 1, "phone": 1 })

// Index for stage queries
db.leads.createIndex({ "type": 1, "order": 1 })
db.leads.createIndex({ "type": 1, "slug": 1 })

// Config query
db.leads.createIndex({ "type": 1, "uid": 1 }, { unique: true })
```

## 🔒 Important Notes

### Single Workflow Constraint
- Only ONE config document (uid="default")
- Check before allowing config creation
- Lock config editing after initial setup

### Lead ID Generation
- Format: LEAD-YYYYMM-XXXXX
- Handle race conditions with retry logic
- Use MongoDB transactions for atomicity

### Stage Transitions
- Always validate `allowed_next_stages`
- Check required tasks are completed
- Exit previous stage before entering new

### Data Validation
- Use Pydantic models for all data
- Validate field values against FieldDefinition
- Type conversion and validation rules

## 🎓 Best Practices

1. **Always use Pydantic models** for MongoDB operations
2. **Embed related data** (tasks, activities) in lead documents
3. **Use transactions** for multi-step operations
4. **Index frequently queried fields**
5. **Paginate list endpoints**
6. **Validate stage transitions**
7. **Maintain activity log** for all changes
8. **Type check custom field values**

## 📚 API Endpoints Summary

```
# Leads
POST   /api/leads/                    # Create lead
GET    /api/leads/                    # List leads
GET    /api/leads/{uid}/              # Get lead details
PATCH  /api/leads/{uid}/              # Update lead
DELETE /api/leads/{uid}/              # Delete lead

# Stage Transitions
POST   /api/leads/{uid}/transition/   # Move to new stage
POST   /api/leads/{uid}/assign/       # Assign to users

# Tasks
GET    /api/leads/{uid}/tasks/        # List tasks
POST   /api/leads/{uid}/tasks/{task_uid}/complete/  # Complete task

# Kanban
GET    /api/leads/kanban/             # Get Kanban data
POST   /api/leads/kanban/move/        # Drag & drop

# Stages
POST   /api/stages/                   # Create stage
GET    /api/stages/                   # List stages
GET    /api/stages/{uid}/             # Get stage
PATCH  /api/stages/{uid}/             # Update stage
DELETE /api/stages/{uid}/             # Delete stage
POST   /api/stages/reorder/           # Reorder stages

# Config
GET    /api/config/                   # Get config
PATCH  /api/config/                   # Update config
```

## 🚧 Next Steps

1. ✅ Copy Pydantic models to your project
2. ✅ Set up MongoDB connection
3. ✅ Implement LeadService with core operations
4. ✅ Create DRF ViewSets and serializers
5. ✅ Initialize sample stages and config
6. ✅ Build Kanban board endpoint
7. ✅ Add authentication (if needed)
8. ✅ Build frontend with drag-drop
9. ✅ Add activity timeline view
10. ✅ Deploy and test!

---

**You now have everything needed to build a fully functional Lead CRM with Kanban board using Django DRF and MongoDB!** 🚀
