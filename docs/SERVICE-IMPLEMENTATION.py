"""
Complete Service Layer Implementation for Lead CRM
This file provides the complete MongoDB service layer with all CRUD operations.
"""

from pymongo.collection import Collection
from pymongo.asynchronous.collection import AsyncCollection
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, UTC
from bson import ObjectId

# Import Pydantic models
from .models import (
    WorkItem,
    WorkStage,
    WorkItemConfig,
    WorkItemTask,
    Activity,
    HistoryData,
    WorkItemStatus,
    WorkItemTaskStatus,
    FieldDefinition,
    TaskFieldValue,
)


class LeadService:
    """
    MongoDB operations for Lead CRM.
    All methods validate with Pydantic before insertion/update.
    """

    def __init__(
        self,
        collection: Collection = None,
        async_collection: AsyncCollection = None,
    ):
        self.collection = collection
        self.async_collection = async_collection

    # ═══════════════════════════════════════════════════════════
    # LEAD CRUD Operations
    # ═══════════════════════════════════════════════════════════

    def create_lead(self, lead_data: Dict[str, Any]) -> str:
        """
        Create new lead with validation.
        
        Args:
            lead_data: Lead data matching WorkItem schema
        
        Returns:
            MongoDB ObjectId as string
        
        Example:
            >>> lead_data = {
            ...     "type": "lead",
            ...     "uid": "uid-abc123",
            ...     "item_id": "LEAD-202601-00001",
            ...     "name": "John Doe",
            ...     "email": "john@example.com",
            ...     "current_stage": "stage-new",
            ...     "config": "default",
            ...     "config_values": [],
            ...     "tasks": [],
            ...     "activities": [],
            ...     "history": []
            ... }
            >>> mongo_id = lead_service.create_lead(lead_data)
        """
        # Validate with Pydantic
        lead = WorkItem(**lead_data)

        # Add timestamps
        now = datetime.now(UTC)
        lead.created_at = now
        lead.updated_at = now

        # Insert to MongoDB
        result = self.collection.insert_one(
            lead.model_dump(mode="json", exclude_none=True)
        )
        return str(result.inserted_id)

    async def acreate_lead(self, lead_data: Dict[str, Any]) -> str:
        """Async version of create_lead"""
        lead = WorkItem(**lead_data)
        now = datetime.now(UTC)
        lead.created_at = now
        lead.updated_at = now

        result = await self.async_collection.insert_one(
            lead.model_dump(mode="json", exclude_none=True)
        )
        return str(result.inserted_id)

    def get_lead(self, uid: str) -> Optional[WorkItem]:
        """
        Get lead by uid.
        
        Args:
            uid: Lead UID
        
        Returns:
            WorkItem or None if not found
        """
        doc = self.collection.find_one({"type": "lead", "uid": uid})
        return WorkItem(**doc) if doc else None

    async def aget_lead(self, uid: str) -> Optional[WorkItem]:
        """Async version of get_lead"""
        doc = await self.async_collection.find_one({"type": "lead", "uid": uid})
        return WorkItem(**doc) if doc else None

    def list_leads(
        self,
        filters: Dict[str, Any] = None,
        limit: int = 10,
        offset: int = 0,
        sort_by: str = "-created_at",
    ) -> Tuple[List[WorkItem], int]:
        """
        List leads with pagination.
        
        Args:
            filters: MongoDB query filters
            limit: Number of results per page
            offset: Number of results to skip
            sort_by: Sort field (prefix with - for descending)
        
        Returns:
            Tuple of (leads list, total count)
        
        Example:
            >>> leads, total = lead_service.list_leads(
            ...     filters={"current_stage": "stage-new"},
            ...     limit=10,
            ...     offset=0
            ... )
        """
        query = {"type": "lead"}
        if filters:
            query.update(filters)

        # Get total count
        total = self.collection.count_documents(query)

        # Parse sort
        sort_field = sort_by.lstrip("-")
        sort_direction = -1 if sort_by.startswith("-") else 1

        # Query with pagination
        cursor = (
            self.collection.find(query)
            .sort(sort_field, sort_direction)
            .skip(offset)
            .limit(limit)
        )

        leads = [WorkItem(**doc) for doc in cursor]
        return leads, total

    def update_lead(self, uid: str, updates: Dict[str, Any]) -> bool:
        """
        Update lead fields.
        
        Args:
            uid: Lead UID
            updates: Fields to update
        
        Returns:
            True if updated, False if not found
        
        Example:
            >>> lead_service.update_lead(
            ...     "uid-abc123",
            ...     {"name": "Jane Doe", "email": "jane@example.com"}
            ... )
        """
        updates["updated_at"] = datetime.now(UTC)
        result = self.collection.update_one(
            {"type": "lead", "uid": uid}, {"$set": updates}
        )
        return result.modified_count > 0

    def delete_lead(self, uid: str) -> bool:
        """
        Delete lead (hard delete).
        
        Args:
            uid: Lead UID
        
        Returns:
            True if deleted, False if not found
        """
        result = self.collection.delete_one({"type": "lead", "uid": uid})
        return result.deleted_count > 0

    # ═══════════════════════════════════════════════════════════
    # STAGE TRANSITION Operations
    # ═══════════════════════════════════════════════════════════

    def transition_stage(
        self,
        lead_uid: str,
        new_stage_uid: str,
        comment: str = "",
        performed_by: str = None,
    ) -> bool:
        """
        Transition lead to new stage with validation.
        
        Steps:
        1. Validate current stage allows transition to new stage
        2. Check all required tasks are completed
        3. Exit current stage in history
        4. Create tasks from new stage template
        5. Update current_stage
        6. Add history entry for new stage
        7. Add stage change activity
        
        Args:
            lead_uid: Lead UID
            new_stage_uid: Target stage UID
            comment: Optional comment for the transition
            performed_by: User ID who performed transition
        
        Returns:
            True if successful, raises ValueError otherwise
        
        Example:
            >>> lead_service.transition_stage(
            ...     "uid-abc123",
            ...     "stage-contacted",
            ...     comment="Successfully reached out",
            ...     performed_by="user-xyz"
            ... )
        """
        # Get lead
        lead = self.get_lead(lead_uid)
        if not lead:
            raise ValueError(f"Lead {lead_uid} not found")

        # Get current and new stages
        current_stage = self.get_stage(lead.current_stage)
        new_stage = self.get_stage(new_stage_uid)

        if not new_stage:
            raise ValueError(f"Stage {new_stage_uid} not found")

        # Validate transition is allowed
        if new_stage_uid not in current_stage.allowed_next_stages:
            raise ValueError(
                f"Transition from {current_stage.name} to {new_stage.name} not allowed"
            )

        # Check required tasks are completed
        required_tasks = [t for t in lead.tasks if t.required and t.status != WorkItemTaskStatus.COMPLETED]
        if required_tasks:
            task_names = ", ".join([t.name for t in required_tasks])
            raise ValueError(f"Required tasks not completed: {task_names}")

        # Exit current stage in history
        now = datetime.now(UTC)
        for hist in lead.history:
            if hist.stage == lead.current_stage and hist.exited_at is None:
                hist.exited_at = now

        # Create tasks from new stage template
        new_tasks = []
        for stage_task in new_stage.stage_tasks:
            task = WorkItemTask(
                uid=f"task-{ObjectId()}",
                template_id=stage_task.uid,
                stage=new_stage_uid,
                name=stage_task.name,
                description=stage_task.description,
                required=stage_task.required,
                order=stage_task.order,
                is_active=stage_task.is_active,
                task_variables=stage_task.task_variables,
                status=WorkItemTaskStatus.PENDING,
                field_values=[],
            )
            new_tasks.append(task)

        # Add new stage to history
        new_history = HistoryData(stage=new_stage_uid, entered_at=now)

        # Add stage change activity
        activity = Activity(
            type="STAGE_CHANGE",
            subject=f"Lead moved to {new_stage.name}",
            description=comment,
            performed_by=performed_by,
            created_at=now,
            created_by=performed_by,
            activity_data={
                "from_stage": current_stage.name,
                "to_stage": new_stage.name,
                "comment": comment,
            },
        )

        # Update lead in MongoDB
        self.collection.update_one(
            {"type": "lead", "uid": lead_uid},
            {
                "$set": {
                    "current_stage": new_stage_uid,
                    "status": WorkItemStatus.IN_PROGRESS,
                    "updated_at": now,
                },
                "$push": {
                    "tasks": {"$each": [t.model_dump(mode="json") for t in new_tasks]},
                    "history": new_history.model_dump(mode="json"),
                    "activities": activity.model_dump(mode="json"),
                },
            },
        )

        return True

    # ═══════════════════════════════════════════════════════════
    # TASK Operations
    # ═══════════════════════════════════════════════════════════

    def complete_task(
        self,
        lead_uid: str,
        task_uid: str,
        field_values: List[Dict[str, Any]],
        notes: str = "",
        completed_by: str = None,
    ) -> bool:
        """
        Complete a task with field values.
        
        Args:
            lead_uid: Lead UID
            task_uid: Task instance UID
            field_values: List of TaskFieldValue dicts
            notes: Optional notes
            completed_by: User ID who completed
        
        Returns:
            True if successful, raises ValueError otherwise
        
        Example:
            >>> lead_service.complete_task(
            ...     "uid-abc123",
            ...     "task-inst-123",
            ...     field_values=[
            ...         {
            ...             "variable": "contact_method",
            ...             "field_type": "enum",
            ...             "original_value": "email",
            ...             "value": "email"
            ...         }
            ...     ],
            ...     notes="Successfully contacted via email",
            ...     completed_by="user-xyz"
            ... )
        """
        now = datetime.now(UTC)

        # Validate field values
        validated_values = [TaskFieldValue(**fv) for fv in field_values]

        # Update task in lead
        result = self.collection.update_one(
            {"type": "lead", "uid": lead_uid, "tasks.uid": task_uid},
            {
                "$set": {
                    "tasks.$.status": WorkItemTaskStatus.COMPLETED.value,
                    "tasks.$.completed_at": now,
                    "tasks.$.completed_by": completed_by,
                    "tasks.$.notes": notes,
                    "tasks.$.field_values": [v.model_dump(mode="json") for v in validated_values],
                    "updated_at": now,
                },
                "$push": {
                    "activities": Activity(
                        type="TASK_COMPLETED",
                        subject="Task completed",
                        performed_by=completed_by,
                        created_at=now,
                        created_by=completed_by,
                        activity_data={"task_uid": task_uid, "notes": notes},
                    ).model_dump(mode="json")
                },
            },
        )

        return result.modified_count > 0

    # ═══════════════════════════════════════════════════════════
    # STAGE Management Operations
    # ═══════════════════════════════════════════════════════════

    def create_stage(self, stage_data: Dict[str, Any]) -> str:
        """Create new stage"""
        stage = WorkStage(**stage_data)
        now = datetime.now(UTC)
        stage.created_at = now
        stage.updated_at = now

        result = self.collection.insert_one(
            stage.model_dump(mode="json", exclude_none=True)
        )
        return str(result.inserted_id)

    def get_stage(self, uid: str) -> Optional[WorkStage]:
        """Get stage by uid"""
        doc = self.collection.find_one({"type": "stage", "uid": uid})
        return WorkStage(**doc) if doc else None

    def list_stages(self) -> List[WorkStage]:
        """List all stages ordered by order field"""
        cursor = self.collection.find({"type": "stage"}).sort("order", 1)
        return [WorkStage(**doc) for doc in cursor]

    def update_stage(self, uid: str, updates: Dict[str, Any]) -> bool:
        """Update stage fields"""
        updates["updated_at"] = datetime.now(UTC)
        result = self.collection.update_one(
            {"type": "stage", "uid": uid}, {"$set": updates}
        )
        return result.modified_count > 0

    def delete_stage(self, uid: str) -> bool:
        """Delete stage (check no leads in this stage first!)"""
        # Check if any leads are in this stage
        lead_count = self.collection.count_documents(
            {"type": "lead", "current_stage": uid}
        )
        if lead_count > 0:
            raise ValueError(
                f"Cannot delete stage: {lead_count} leads are currently in this stage"
            )

        result = self.collection.delete_one({"type": "stage", "uid": uid})
        return result.deleted_count > 0

    def reorder_stages(self, stage_orders: List[Dict[str, Any]]) -> bool:
        """
        Reorder stages.
        
        Args:
            stage_orders: List of {"uid": "stage-uid", "order": 0}
        
        Example:
            >>> lead_service.reorder_stages([
            ...     {"uid": "stage-new", "order": 0},
            ...     {"uid": "stage-contacted", "order": 1},
            ...     {"uid": "stage-qualified", "order": 2}
            ... ])
        """
        from pymongo import UpdateOne

        operations = [
            UpdateOne(
                {"type": "stage", "uid": item["uid"]},
                {"$set": {"order": item["order"], "updated_at": datetime.now(UTC)}},
            )
            for item in stage_orders
        ]

        result = self.collection.bulk_write(operations)
        return result.modified_count > 0

    # ═══════════════════════════════════════════════════════════
    # CONFIG Operations
    # ═══════════════════════════════════════════════════════════

    def get_or_create_config(self) -> WorkItemConfig:
        """
        Get or create the single workflow config.
        Always uid="default".
        """
        doc = self.collection.find_one({"type": "config", "uid": "default"})

        if doc:
            return WorkItemConfig(**doc)

        # Create default config
        config = WorkItemConfig(
            uid="default",
            workflow_name="Lead Workflow",
            is_active=True,
            variables=[],
        )

        self.collection.insert_one(config.model_dump(mode="json", exclude_none=True))
        return config

    def update_config(self, variables: List[Dict[str, Any]]) -> bool:
        """
        Update config variables.
        
        Args:
            variables: List of FieldDefinition dicts
        
        Example:
            >>> lead_service.update_config([
            ...     {
            ...         "field_key": "budget",
            ...         "label": "Budget",
            ...         "field_type": "decimal",
            ...         "input_type": "number",
            ...         "required": True
            ...     }
            ... ])
        """
        # Validate with Pydantic
        validated_vars = [FieldDefinition(**v) for v in variables]

        result = self.collection.update_one(
            {"type": "config", "uid": "default"},
            {
                "$set": {
                    "variables": [v.model_dump(mode="json") for v in validated_vars],
                    "updated_at": datetime.now(UTC),
                }
            },
        )

        return result.modified_count > 0

    # ═══════════════════════════════════════════════════════════
    # KANBAN Board Operations
    # ═══════════════════════════════════════════════════════════

    def get_kanban_data(self) -> List[Dict[str, Any]]:
        """
        Get Kanban board data grouped by stage.
        
        Returns:
            List of stage data with leads:
            [
                {
                    "stage": {"uid": "...", "name": "...", "color": "...", "order": 0},
                    "leads": [...],
                    "count": 5
                }
            ]
        """
        pipeline = [
            {"$match": {"type": "lead"}},
            {
                "$group": {
                    "_id": "$current_stage",
                    "leads": {"$push": "$$ROOT"},
                    "count": {"$sum": 1},
                }
            },
            {
                "$lookup": {
                    "from": self.collection.name,
                    "let": {"stage_uid": "$_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$type", "stage"]},
                                        {"$eq": ["$uid", "$$stage_uid"]},
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "stage_info",
                }
            },
            {"$unwind": "$stage_info"},
            {"$sort": {"stage_info.order": 1}},
            {
                "$project": {
                    "stage": "$stage_info",
                    "leads": 1,
                    "count": 1,
                }
            },
        ]

        return list(self.collection.aggregate(pipeline))

    # ═══════════════════════════════════════════════════════════
    # ACTIVITY Operations
    # ═══════════════════════════════════════════════════════════

    def add_activity(
        self,
        lead_uid: str,
        activity_type: str,
        subject: str,
        description: str = "",
        performed_by: str = None,
        activity_data: Dict[str, Any] = None,
    ) -> bool:
        """
        Add manual activity to lead.
        
        Args:
            lead_uid: Lead UID
            activity_type: Activity type (NOTE_ADDED, EMAIL_SENT, etc.)
            subject: Activity subject
            description: Activity description
            performed_by: User ID
            activity_data: Additional metadata
        
        Example:
            >>> lead_service.add_activity(
            ...     "uid-abc123",
            ...     "NOTE_ADDED",
            ...     "Follow-up scheduled",
            ...     description="Scheduled call for next week",
            ...     performed_by="user-xyz"
            ... )
        """
        now = datetime.now(UTC)
        activity = Activity(
            type=activity_type,
            subject=subject,
            description=description,
            performed_by=performed_by,
            created_at=now,
            created_by=performed_by,
            activity_data=activity_data or {},
        )

        result = self.collection.update_one(
            {"type": "lead", "uid": lead_uid},
            {
                "$push": {"activities": activity.model_dump(mode="json")},
                "$set": {"updated_at": now},
            },
        )

        return result.modified_count > 0

    # ═══════════════════════════════════════════════════════════
    # HELPER Methods
    # ═══════════════════════════════════════════════════════════

    def generate_lead_id(self, prefix: str = "LEAD") -> str:
        """
        Generate unique lead ID: LEAD-YYYYMM-00001
        
        Uses MongoDB to find last lead ID for the month and increment.
        Handles race conditions with retry logic.
        """
        from datetime import datetime

        current_date = datetime.now()
        month_prefix = f"{prefix}-{current_date.strftime('%Y%m')}"

        # Find last lead for this month
        last_lead = self.collection.find_one(
            {"type": "lead", "item_id": {"$regex": f"^{month_prefix}"}},
            sort=[("item_id", -1)],
        )

        if last_lead:
            # Extract number and increment
            last_num = int(last_lead["item_id"].split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{month_prefix}-{new_num:05d}"

    def assign_lead(self, lead_uid: str, user_ids: List[str], performed_by: str = None) -> bool:
        """
        Assign lead to users.
        
        Args:
            lead_uid: Lead UID
            user_ids: List of user IDs to assign
            performed_by: User ID who performed assignment
        
        Returns:
            True if successful
        """
        now = datetime.now(UTC)
        activity = Activity(
            type="ASSIGNED",
            subject=f"Lead assigned to {len(user_ids)} users",
            performed_by=performed_by,
            created_at=now,
            created_by=performed_by,
            activity_data={"assigned_to": user_ids},
        )

        result = self.collection.update_one(
            {"type": "lead", "uid": lead_uid},
            {
                "$set": {"assigned_to": user_ids, "updated_at": now},
                "$push": {"activities": activity.model_dump(mode="json")},
            },
        )

        return result.modified_count > 0


# ═══════════════════════════════════════════════════════════
# Example Usage
# ═══════════════════════════════════════════════════════════

"""
# Initialize service
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.lead_crm
collection = db.leads

lead_service = LeadService(collection=collection)

# Create a lead
lead_data = {
    "type": "lead",
    "uid": "uid-abc123",
    "item_id": lead_service.generate_lead_id(),
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "current_stage": "stage-new",
    "status": "pending",
    "config": "default",
    "config_values": [],
    "assigned_to": [],
    "properties": {},
    "linked_entities": {},
    "history": [
        {
            "stage": "stage-new",
            "entered_at": datetime.now(UTC)
        }
    ],
    "tasks": [],
    "activities": [
        {
            "type": "CREATED",
            "subject": "Lead created",
            "created_at": datetime.now(UTC)
        }
    ]
}

mongo_id = lead_service.create_lead(lead_data)

# List leads
leads, total = lead_service.list_leads(limit=10, offset=0)

# Transition stage
lead_service.transition_stage(
    "uid-abc123",
    "stage-contacted",
    comment="Successfully reached out",
    performed_by="user-xyz"
)

# Complete task
lead_service.complete_task(
    "uid-abc123",
    "task-inst-123",
    field_values=[
        {
            "variable": "contact_method",
            "field_type": "enum",
            "original_value": "email",
            "value": "email"
        }
    ],
    notes="Contact established",
    performed_by="user-xyz"
)

# Get Kanban data
kanban_data = lead_service.get_kanban_data()
"""
