from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from lead_crm.database import leads_collection, stages_collection, configs_collection
from .services import LeadService
from .serializers import (
    WorkItemSerializer,
    WorkStageSerializer,
    WorkItemConfigSerializer,
    LeadCreateSerializer,
    LeadUpdateSerializer,
    StageTransitionSerializer,
    TaskCompleteSerializer,
    ActivityAddSerializer,
    StageReorderSerializer,
)


class LeadViewSet(ViewSet):
    """ViewSet for Lead CRUD and operations"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = LeadService(
            leads_collection, stages_collection, configs_collection
        )

    def list(self, request):
        """List all leads with pagination"""
        limit = int(request.query_params.get("limit", 100))
        offset = int(request.query_params.get("offset", 0))

        # Build filters from query params
        filters = {}
        if "config" in request.query_params:
            filters["config"] = request.query_params["config"]
        if "current_stage" in request.query_params:
            filters["current_stage"] = request.query_params["current_stage"]
        if "status" in request.query_params:
            filters["status"] = request.query_params["status"]

        leads, total = self.service.list_leads(
            filters=filters, limit=limit, offset=offset
        )

        serializer = WorkItemSerializer(
            [lead.model_dump() for lead in leads], many=True
        )
        return Response(
            {
                "results": serializer.data,
                "count": total,
                "limit": limit,
                "offset": offset,
            }
        )

    def retrieve(self, request, pk=None):
        """Get a specific lead by UID"""
        lead = self.service.get_lead(pk)
        if not lead:
            return Response(
                {"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = WorkItemSerializer(lead.model_dump())
        return Response(serializer.data)

    def create(self, request):
        """Create new lead"""
        serializer = LeadCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            lead_id = self.service.create_lead(serializer.validated_data)

            # Fetch created lead
            uid = serializer.validated_data.get("uid", None)
            if not uid:
                # If uid wasn't provided, we need to get it from the created lead
                created_lead = self.service.collection.find_one({"_id": lead_id})
                uid = created_lead["uid"]

            lead = self.service.get_lead(uid)
            response_serializer = WorkItemSerializer(lead.model_dump())
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Update lead"""
        serializer = LeadUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            success = self.service.update_lead(pk, serializer.validated_data)
            if not success:
                return Response(
                    {"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND
                )

            lead = self.service.get_lead(pk)
            response_serializer = WorkItemSerializer(lead.model_dump())
            return Response(response_serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """Delete lead"""
        success = self.service.delete_lead(pk)
        if not success:
            return Response(
                {"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="kanban")
    def kanban(self, request):
        """Get Kanban board data"""
        data = self.service.get_kanban_data()
        return Response(data)

    @action(detail=True, methods=["post"], url_path="transition")
    def transition(self, request, pk=None):
        """Transition lead to new stage"""
        serializer = StageTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.service.transition_stage(
                pk,
                serializer.validated_data["to_stage"],
                serializer.validated_data.get("comment", ""),
                serializer.validated_data.get("performed_by"),
            )

            lead = self.service.get_lead(pk)
            response_serializer = WorkItemSerializer(lead.model_dump())
            return Response(response_serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True, methods=["post"], url_path="tasks/(?P<task_uid>[^/.]+)/complete"
    )
    def complete_task(self, request, pk=None, task_uid=None):
        """Complete a task"""
        serializer = TaskCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            success = self.service.complete_task(
                pk,
                task_uid,
                serializer.validated_data.get("field_values", []),
                serializer.validated_data.get("notes", ""),
                serializer.validated_data.get("completed_by"),
            )

            if not success:
                return Response(
                    {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
                )

            lead = self.service.get_lead(pk)
            response_serializer = WorkItemSerializer(lead.model_dump())
            return Response(response_serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="activities")
    def add_activity(self, request, pk=None):
        """Add an activity to lead"""
        serializer = ActivityAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            success = self.service.add_activity(
                pk,
                serializer.validated_data["type"],
                serializer.validated_data["subject"],
                serializer.validated_data.get("description", ""),
                serializer.validated_data.get("performed_by"),
                serializer.validated_data.get("activity_data", {}),
            )

            if not success:
                return Response(
                    {"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND
                )

            return Response({"message": "Activity added"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StageViewSet(ViewSet):
    """ViewSet for Stage management"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = LeadService(
            leads_collection, stages_collection, configs_collection
        )

    def list(self, request):
        """List all stages"""
        stages = self.service.list_stages()
        serializer = WorkStageSerializer(
            [stage.model_dump() for stage in stages], many=True
        )
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Get a specific stage by UID"""
        stage = self.service.get_stage(pk)
        if not stage:
            return Response(
                {"error": "Stage not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = WorkStageSerializer(stage.model_dump())
        return Response(serializer.data)

    def create(self, request):
        """Create new stage"""
        serializer = WorkStageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            stage_id = self.service.create_stage(serializer.validated_data)

            # Fetch created stage
            uid = serializer.validated_data.get("uid", None)
            if not uid:
                created_stage = self.service.collection.find_one({"_id": stage_id})
                uid = created_stage["uid"]

            stage = self.service.get_stage(uid)
            response_serializer = WorkStageSerializer(stage.model_dump())
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Update stage"""
        serializer = WorkStageSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            success = self.service.update_stage(pk, serializer.validated_data)
            if not success:
                return Response(
                    {"error": "Stage not found"}, status=status.HTTP_404_NOT_FOUND
                )

            stage = self.service.get_stage(pk)
            response_serializer = WorkStageSerializer(stage.model_dump())
            return Response(response_serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """Delete stage"""
        try:
            success = self.service.delete_stage(pk)
            if not success:
                return Response(
                    {"error": "Stage not found"}, status=status.HTTP_404_NOT_FOUND
                )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="reorder")
    def reorder(self, request):
        """Reorder stages"""
        serializer = StageReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.service.reorder_stages(serializer.validated_data["stage_orders"])
            return Response({"message": "Stages reordered"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ConfigViewSet(ViewSet):
    """ViewSet for Workflow Config"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = LeadService(
            leads_collection, stages_collection, configs_collection
        )

    def list(self, request):
        """Get all workflow configs"""
        configs = self.service.list_configs()
        serializer = WorkItemConfigSerializer(
            [config.model_dump() for config in configs], many=True
        )
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Get specific workflow config"""
        config = self.service.get_config(pk)
        if not config:
            return Response(
                {"error": "Config not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = WorkItemConfigSerializer(config.model_dump())
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Update workflow config"""
        serializer = WorkItemConfigSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            success = self.service.update_config(pk, serializer.validated_data)
            if not success:
                return Response(
                    {"error": "Config not found"}, status=status.HTTP_404_NOT_FOUND
                )

            config = self.service.get_config(pk)
            response_serializer = WorkItemConfigSerializer(config.model_dump())
            return Response(response_serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        """Create new workflow config"""
        serializer = WorkItemConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            config_id = self.service.create_config(serializer.validated_data)
            uid = serializer.validated_data.get("uid")

            config = self.service.get_config(uid)
            response_serializer = WorkItemConfigSerializer(config.model_dump())
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
