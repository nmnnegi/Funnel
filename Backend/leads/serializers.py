from rest_framework import serializers
from typing import Dict, Any, List


class FieldDefinitionSerializer(serializers.Serializer):
    """Serializer for FieldDefinition"""

    field_key = serializers.CharField()
    label = serializers.CharField()
    field_type = serializers.ChoiceField(
        choices=[
            "string",
            "integer",
            "decimal",
            "boolean",
            "date",
            "datetime",
            "enum",
            "array",
            "document",
        ]
    )
    input_type = serializers.ChoiceField(
        choices=[
            "text",
            "textarea",
            "number",
            "dropdown",
            "multi_select",
            "radio",
            "checkbox",
            "date_picker",
            "datetime_picker",
            "email",
            "phone",
            "url",
            "file_upload",
        ]
    )
    required = serializers.BooleanField(default=False)
    options = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    default_value = serializers.CharField(required=False, allow_null=True)
    validation_rules = serializers.DictField(required=False, default=dict)
    placeholder = serializers.CharField(required=False, default="")
    help_text = serializers.CharField(required=False, default="")
    order = serializers.IntegerField(default=0)
    is_active = serializers.BooleanField(default=True)
    array_item_type = serializers.CharField(required=False, allow_null=True)


class ConfigFieldValueSerializer(serializers.Serializer):
    """Serializer for ConfigFieldValue"""

    variable = serializers.CharField()
    field_type = serializers.CharField()
    original_value = serializers.CharField(default="")
    value = serializers.JSONField(required=False, allow_null=True)


class TaskFieldValueSerializer(serializers.Serializer):
    """Serializer for TaskFieldValue"""

    variable = serializers.CharField()
    field_type = serializers.CharField()
    original_value = serializers.CharField(default="")
    value = serializers.JSONField(required=False, allow_null=True)


class WorkStageTaskSerializer(serializers.Serializer):
    """Serializer for WorkStageTask"""

    uid = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_null=True)
    required = serializers.BooleanField(default=False)
    order = serializers.IntegerField(default=0)
    is_active = serializers.BooleanField(default=True)
    task_variables = FieldDefinitionSerializer(many=True, required=False)


class WorkItemTaskSerializer(serializers.Serializer):
    """Serializer for WorkItemTask"""

    uid = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_null=True)
    template_id = serializers.CharField()
    stage = serializers.CharField()
    status = serializers.ChoiceField(
        choices=["pending", "in_progress", "completed", "skipped", "blocked"],
        default="pending",
    )
    required = serializers.BooleanField(default=False)
    order = serializers.IntegerField(default=0)
    is_active = serializers.BooleanField(default=True)
    task_variables = FieldDefinitionSerializer(many=True, required=False)
    completed_at = serializers.DateTimeField(required=False, allow_null=True)
    completed_by = serializers.CharField(required=False, allow_null=True)
    notes = serializers.CharField(default="")
    field_values = TaskFieldValueSerializer(many=True, required=False)


class ActivitySerializer(serializers.Serializer):
    """Serializer for Activity"""

    type = serializers.CharField()
    subject = serializers.CharField()
    description = serializers.CharField(required=False, allow_null=True)
    performed_by = serializers.CharField(required=False, allow_null=True)
    created_at = serializers.DateTimeField()
    created_by = serializers.CharField(required=False, allow_null=True)
    activity_data = serializers.DictField(required=False, default=dict)


class HistoryDataSerializer(serializers.Serializer):
    """Serializer for HistoryData"""

    stage = serializers.CharField()
    entered_at = serializers.DateTimeField()
    exited_at = serializers.DateTimeField(required=False, allow_null=True)


class WorkStageSerializer(serializers.Serializer):
    """Serializer for WorkStage"""

    uid = serializers.CharField(required=False)
    name = serializers.CharField()
    slug = serializers.CharField()
    color = serializers.CharField(default="#6B7280")
    description = serializers.CharField(required=False, allow_null=True)
    order = serializers.IntegerField(default=0)
    is_active = serializers.BooleanField(default=True)
    allowed_next_stages = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    stage_tasks = WorkStageTaskSerializer(many=True, required=False)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)


class WorkItemSerializer(serializers.Serializer):
    """Serializer for WorkItem (Lead)"""

    uid = serializers.CharField(required=False)
    item_id = serializers.CharField(required=False)
    current_stage = serializers.CharField()
    status = serializers.ChoiceField(
        choices=["pending", "in_progress", "completed", "skipped", "blocked"],
        default="pending",
    )
    name = serializers.CharField()
    email = serializers.EmailField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True)
    config = serializers.CharField(default="default")
    config_values = ConfigFieldValueSerializer(many=True, required=False)
    assigned_to = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    properties = serializers.DictField(required=False, default=dict)
    linked_entities = serializers.DictField(required=False, default=dict)
    history = HistoryDataSerializer(many=True, required=False)
    tasks = WorkItemTaskSerializer(many=True, required=False)
    activities = ActivitySerializer(many=True, required=False)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)
    created_by = serializers.CharField(required=False, allow_null=True)


class WorkItemConfigSerializer(serializers.Serializer):
    """Serializer for WorkItemConfig"""

    uid = serializers.CharField(default="default")
    workflow_name = serializers.CharField(default="Lead Workflow")
    is_active = serializers.BooleanField(default=True)
    variables = FieldDefinitionSerializer(many=True, required=False)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)


# Request/Response Serializers


class LeadCreateSerializer(serializers.Serializer):
    """Serializer for creating a lead"""

    name = serializers.CharField()
    email = serializers.EmailField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True)
    current_stage = serializers.CharField()
    config_values = ConfigFieldValueSerializer(many=True, required=False, default=list)
    assigned_to = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    created_by = serializers.CharField(required=False, allow_null=True)


class LeadUpdateSerializer(serializers.Serializer):
    """Serializer for updating a lead"""

    name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True)
    config_values = ConfigFieldValueSerializer(many=True, required=False)
    assigned_to = serializers.ListField(child=serializers.CharField(), required=False)
    properties = serializers.DictField(required=False)


class StageTransitionSerializer(serializers.Serializer):
    """Serializer for stage transition"""

    to_stage = serializers.CharField()
    comment = serializers.CharField(required=False, default="")
    performed_by = serializers.CharField(required=False, allow_null=True)


class TaskCompleteSerializer(serializers.Serializer):
    """Serializer for completing a task"""

    field_values = TaskFieldValueSerializer(many=True, required=False, default=list)
    notes = serializers.CharField(required=False, default="")
    completed_by = serializers.CharField(required=False, allow_null=True)


class ActivityAddSerializer(serializers.Serializer):
    """Serializer for adding an activity"""

    type = serializers.CharField()
    subject = serializers.CharField()
    description = serializers.CharField(required=False, default="")
    performed_by = serializers.CharField(required=False, allow_null=True)
    activity_data = serializers.DictField(required=False, default=dict)


class StageReorderSerializer(serializers.Serializer):
    """Serializer for reordering stages"""

    stage_orders = serializers.ListField(child=serializers.DictField())
