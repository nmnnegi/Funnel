from pymongo.collection import Collection
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, UTC
from bson import ObjectId
import uuid

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
    generate_lead_id,
)


class LeadService:
    """MongoDB operations for Lead CRM"""

    def __init__(
        self, leads_col: Collection, stages_col: Collection, configs_col: Collection
    ):
        self.leads_collection = leads_col
        self.stages_collection = stages_col
        self.configs_collection = configs_col

    def create_lead(self, lead_data: Dict[str, Any]) -> str:
        """Create new lead with validation"""
        # Generate UID and item_id if not provided
        if "uid" not in lead_data:
            lead_data["uid"] = str(uuid.uuid4())
        if "item_id" not in lead_data:
            lead_data["item_id"] = generate_lead_id(self.leads_collection)

        # Validate with Pydantic
        lead = WorkItem(**lead_data)

        # Add timestamps
        now = datetime.now(UTC)
        lead.created_at = now
        lead.updated_at = now

        # Add initial history entry
        if not lead.history and lead.current_stage:
            lead.history.append(HistoryData(stage=lead.current_stage, entered_at=now))

        # Add creation activity
        if not lead.activities:
            lead.activities.append(
                Activity(
                    type="CREATED",
                    subject="Lead created",
                    performed_by=lead.created_by,
                    created_at=now,
                    created_by=lead.created_by,
                )
            )

        # Insert to MongoDB
        result = self.leads_collection.insert_one(
            lead.model_dump(mode="json", exclude_none=True, by_alias=True)
        )
        return str(result.inserted_id)

    def get_lead(self, uid: str) -> Optional[WorkItem]:
        """Get lead by uid"""
        doc = self.leads_collection.find_one({"uid": uid})
        return WorkItem(**doc) if doc else None

    def list_leads(
        self,
        filters: Dict[str, Any] = None,
        limit: int = 10,
        offset: int = 0,
        sort_by: str = "-created_at",
    ) -> Tuple[List[WorkItem], int]:
        """List leads with pagination"""
        query = {}
        if filters:
            query.update(filters)

        # Get total count
        total = self.leads_collection.count_documents(query)

        # Parse sort
        sort_field = sort_by.lstrip("-")
        sort_direction = -1 if sort_by.startswith("-") else 1

        # Query with pagination
        cursor = (
            self.leads_collection.find(query)
            .sort(sort_field, sort_direction)
            .skip(offset)
            .limit(limit)
        )

        leads = [WorkItem(**doc) for doc in cursor]
        return leads, total

    def update_lead(self, uid: str, updates: Dict[str, Any]) -> bool:
        """Update lead fields"""
        updates["updated_at"] = datetime.now(UTC)
        result = self.leads_collection.update_one({"uid": uid}, {"$set": updates})
        return result.modified_count > 0

    def delete_lead(self, uid: str) -> bool:
        """Delete lead (hard delete)"""
        result = self.leads_collection.delete_one({"uid": uid})
        return result.deleted_count > 0

    def transition_stage(
        self,
        lead_uid: str,
        new_stage_uid: str,
        comment: str = "",
        performed_by: str = None,
    ) -> bool:
        """Transition lead to new stage with validation"""
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
        required_tasks = [
            t
            for t in lead.tasks
            if t.required and t.status != WorkItemTaskStatus.COMPLETED
        ]
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
                uid=str(uuid.uuid4()),
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
        self.leads_collection.update_one(
            {"uid": lead_uid},
            {
                "$set": {
                    "current_stage": new_stage_uid,
                    "status": WorkItemStatus.IN_PROGRESS.value,
                    "updated_at": now,
                    "history": [h.model_dump(mode="json") for h in lead.history],
                },
                "$push": {
                    "tasks": {"$each": [t.model_dump(mode="json") for t in new_tasks]},
                    "activities": activity.model_dump(mode="json"),
                },
            },
        )

        return True

    def complete_task(
        self,
        lead_uid: str,
        task_uid: str,
        field_values: List[Dict[str, Any]],
        notes: str = "",
        completed_by: str = None,
    ) -> bool:
        """Complete a task with field values"""
        now = datetime.now(UTC)

        # Validate field values
        validated_values = [TaskFieldValue(**fv) for fv in field_values]

        # Update task in lead
        result = self.leads_collection.update_one(
            {"uid": lead_uid, "tasks.uid": task_uid},
            {
                "$set": {
                    "tasks.$.status": WorkItemTaskStatus.COMPLETED.value,
                    "tasks.$.completed_at": now,
                    "tasks.$.completed_by": completed_by,
                    "tasks.$.notes": notes,
                    "tasks.$.field_values": [
                        v.model_dump(mode="json") for v in validated_values
                    ],
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

    def create_stage(self, stage_data: Dict[str, Any]) -> str:
        """Create new stage"""
        # Generate UID if not provided
        if "uid" not in stage_data:
            stage_data["uid"] = str(uuid.uuid4())

        stage = WorkStage(**stage_data)
        now = datetime.now(UTC)
        stage.created_at = now
        stage.updated_at = now

        result = self.stages_collection.insert_one(
            stage.model_dump(mode="json", exclude_none=True, by_alias=True)
        )
        return str(result.inserted_id)

    def get_stage(self, uid: str) -> Optional[WorkStage]:
        """Get stage by uid"""
        doc = self.stages_collection.find_one({"uid": uid})
        return WorkStage(**doc) if doc else None

    def list_stages(self, config_uid: str = None) -> List[WorkStage]:
        """List all stages, optionally filtered by config"""
        query = {}
        if config_uid:
            query["config"] = config_uid
        cursor = self.stages_collection.find(query).sort("order", 1)
        return [WorkStage(**doc) for doc in cursor]

    def update_stage(self, uid: str, updates: Dict[str, Any]) -> bool:
        """Update stage fields"""
        updates["updated_at"] = datetime.now(UTC)
        result = self.stages_collection.update_one({"uid": uid}, {"$set": updates})
        return result.modified_count > 0

    def delete_stage(self, uid: str) -> bool:
        """Delete stage (check no leads in this stage first!)"""
        # Check if any leads are in this stage
        lead_count = self.leads_collection.count_documents({"current_stage": uid})
        if lead_count > 0:
            raise ValueError(
                f"Cannot delete stage: {lead_count} leads are currently in this stage"
            )

        result = self.stages_collection.delete_one({"uid": uid})
        return result.deleted_count > 0

    def reorder_stages(self, stage_orders: List[Dict[str, Any]]) -> bool:
        """Reorder stages"""
        from pymongo import UpdateOne

        operations = [
            UpdateOne(
                {"uid": item["uid"]},
                {"$set": {"order": item["order"], "updated_at": datetime.now(UTC)}},
            )
            for item in stage_orders
        ]

        result = self.stages_collection.bulk_write(operations)
        return result.modified_count > 0

    def get_config(self, uid: str) -> Optional[WorkItemConfig]:
        """Get workflow config by UID"""
        doc = self.configs_collection.find_one({"uid": uid})
        return WorkItemConfig(**doc) if doc else None

    def list_configs(self) -> List[WorkItemConfig]:
        """List all workflow configs"""
        cursor = self.configs_collection.find({})
        return [WorkItemConfig(**doc) for doc in cursor]

    def create_config(self, config_data: Dict[str, Any]) -> str:
        """Create new workflow config"""
        if "uid" not in config_data:
            config_data["uid"] = str(uuid.uuid4())

        config = WorkItemConfig(**config_data)
        now = datetime.now(UTC)
        config.created_at = now
        config.updated_at = now

        result = self.configs_collection.insert_one(
            config.model_dump(mode="json", exclude_none=True, by_alias=True)
        )
        return str(result.inserted_id)

    def get_or_create_config(self, uid: str = "default") -> WorkItemConfig:
        """Get or create a workflow config"""
        doc = self.configs_collection.find_one({"uid": uid})

        if doc:
            return WorkItemConfig(**doc)

        # Create default config
        config = WorkItemConfig(
            uid=uid,
            workflow_name=f"Workflow {uid}",
            is_active=True,
            variables=[],
        )

        self.configs_collection.insert_one(
            config.model_dump(mode="json", exclude_none=True, by_alias=True)
        )
        return config

    def update_config(self, uid: str, updates: Dict[str, Any]) -> bool:
        """Update config"""
        if "variables" in updates:
            # Validate with Pydantic
            validated_vars = [FieldDefinition(**v) for v in updates["variables"]]
            updates["variables"] = [v.model_dump(mode="json") for v in validated_vars]

        updates["updated_at"] = datetime.now(UTC)
        result = self.configs_collection.update_one({"uid": uid}, {"$set": updates})
        return result.modified_count > 0

    def get_kanban_data(self, config_uid: str = None) -> List[Dict[str, Any]]:
        """Get Kanban board data grouped by stage"""
        # Get stages for this config
        stages = self.list_stages(config_uid)

        # Then, get leads for each stage
        kanban_data = []
        for stage in stages:
            query = {"current_stage": stage.uid}
            if config_uid:
                query["config"] = config_uid

            leads_cursor = self.leads_collection.find(query)
            leads = [WorkItem(**doc) for doc in leads_cursor]

            kanban_data.append(
                {
                    "stage": stage.model_dump(mode="json"),
                    "leads": [lead.model_dump(mode="json") for lead in leads],
                    "count": len(leads),
                }
            )

        return kanban_data

    def add_activity(
        self,
        lead_uid: str,
        activity_type: str,
        subject: str,
        description: str = "",
        performed_by: str = None,
        activity_data: Dict[str, Any] = None,
    ) -> bool:
        """Add activity to lead"""
        activity = Activity(
            type=activity_type,
            subject=subject,
            description=description,
            performed_by=performed_by,
            created_at=datetime.now(UTC),
            created_by=performed_by,
            activity_data=activity_data or {},
        )

        result = self.leads_collection.update_one(
            {"uid": lead_uid},
            {
                "$push": {"activities": activity.model_dump(mode="json")},
                "$set": {"updated_at": datetime.now(UTC)},
            },
        )

        return result.modified_count > 0
