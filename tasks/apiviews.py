from django.contrib.auth.models import User
from django_filters.rest_framework import (
    CharFilter,
    ChoiceFilter,
    DjangoFilterBackend,
    FilterSet,
    BooleanFilter,
    IsoDateTimeFilter,
)

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from tasks.models import Task, TaskHistory

STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("IN_PROGRESS", "IN_PROGRESS"),
    ("COMPLETED", "COMPLETED"),
    ("CANCELLED", "CANCELLED"),
)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username")


class TaskFilter(FilterSet):
    title = CharFilter(lookup_expr="icontains")
    status = ChoiceFilter(choices=STATUS_CHOICES)
    completed = BooleanFilter()


class TaskSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ["id", "title", "description", "completed", "status", "user"]


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    permission_classes = (IsAuthenticated,)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, deleted=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskListAPI(APIView):
    def get(self, request):
        tasks = Task.objects.filter(deleted=False)
        data = TaskSerializer(tasks, many=True).data
        return Response({"tasks": data})


class TaskHistoryFilter(FilterSet):
    updated_at = IsoDateTimeFilter()
    previous_status = ChoiceFilter(choices=STATUS_CHOICES)
    current_status = ChoiceFilter(choices=STATUS_CHOICES)


class TaskHistorySerializer(ModelSerializer):
    class Meta:
        model = TaskHistory
        fields = ["previous_status", "current_status", "updated_at"]


class TaskHistoryViewSet(ReadOnlyModelViewSet):
    queryset = TaskHistory.objects.all()
    serializer_class = TaskHistorySerializer

    permission_classes = (IsAuthenticated,)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskHistoryFilter

    def get_queryset(self):
        task_id = self.kwargs["id"]
        return TaskHistory.objects.filter(
            task=task_id, task__deleted=False, task__user=self.request.user
        )
