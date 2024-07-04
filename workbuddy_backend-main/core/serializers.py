from rest_framework import serializers
from .models import Project, ProjectTeamMember
from users.serializers import ManagerSerializer, EmployeeSerializer

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description']

class ProjectCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['name', 'description', 'end_date']

class ProjectTeamMemberSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer()
    class Meta:
        model = ProjectTeamMember
        fields = ['id', 'employee', 'joined_at']

class ProjectDetailSerializer(serializers.ModelSerializer):
    manager = ManagerSerializer()
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'status', 'manager']