from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ProjectSerializer, ProjectCreationSerializer, ProjectDetailSerializer, ProjectTeamMemberSerializer
from users.serializers import EmployeeDetailSerializer, SkillSerializer
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework.authentication import TokenAuthentication
from .models import Project, ProjectTeamMember, Ticket
from users.models import Employee, Manager, Skill, UserDetail

User = get_user_model()

class ProjectListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'MANAGER':
            projects = Project.objects.filter(manager=request.user)
            serializer = ProjectSerializer(projects, many=True)
            return Response(serializer.data)
        elif request.user.role == 'EMPLOYEE':
            project_tms = ProjectTeamMember.objects.filter(employee=request.user).values_list('project')
            projects = Project.objects.filter(id__in=project_tms)
            serializer = ProjectSerializer(projects, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)

class ProjectCreationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role == 'MANAGER':
            serializer = ProjectCreationSerializer(data=request.data)
            if serializer.is_valid():
                project = serializer.save(manager=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
        
class ProjectDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_project(self, id):
        try:
            model = Project.objects.get(id=id)
            return model
        except Project.DoesNotExist:
            return

    def get(self, request, id):
        project = self.get_project(id)
        if not project:
            return Response(f'Project with id {id} is not found', status=status.HTTP_404_NOT_FOUND)

        user_role = request.user.role
        if user_role == 'MANAGER' and project.manager == request.user:
            serializer = ProjectDetailSerializer(project)
        elif user_role == 'EMPLOYEE':
            project_tms = ProjectTeamMember.objects.filter(employee=request.user, project=project)
            if project_tms.exists():
                serializer = ProjectDetailSerializer(project)
            else:
                return Response({'error': 'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
            
        return Response(serializer.data)

    def put(self, request, id):
        if request.user.role == 'MANAGER':
            serializer = ProjectDetailSerializer(self.get_project(id), data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, id):
        model = self.get_project(id)
        model.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProjectTeamMemberView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        if request.user.role == 'MANAGER':
            project = Project.objects.get(id=id)
            project_team_members = ProjectTeamMember.objects.filter(project=project)
            serializer = ProjectTeamMemberSerializer(project_team_members, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)

class AddTMView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        if request.user.role == User.Role.MANAGER:
            project = get_object_or_404(Project, id=id)
            employee_ids = project.project_team_members.values_list('employee__id', flat=True)
            user_list = Employee.objects.filter(role='EMPLOYEE').exclude(id__in=employee_ids)
            employees = UserDetail.objects.filter(user__in=user_list)
            serializer = EmployeeDetailSerializer(employees, many=True)
            print(serializer.data)
            return Response(serializer.data)
        else:
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, id):
        if request.user.role == User.Role.MANAGER:
            project = get_object_or_404(Project, id=id)
            employee_ids = project.project_team_members.values_list('employee__id', flat=True)
            employees = Employee.objects.exclude(id__in=employee_ids)
            employee_list = request.data.get('employees', [])

            if not isinstance(employee_list, list):
                return Response({'error': 'Invalid employee list'}, status=status.HTTP_400_BAD_REQUEST)

            team_members = []
            for employee_id in employee_list:
                employee = employees.exclude(id=employee_id).first()   
                if employee:
                    team_member = ProjectTeamMember(employee=employee, project=project)
                    team_members.append(team_member)
                else:
                    return Response({'error': f'Invalid employee ID: {employee_id}'}, status=status.HTTP_400_BAD_REQUEST)

            print(team_members)
            ProjectTeamMember.objects.bulk_create(team_members)
            serializer = ProjectTeamMemberSerializer(team_members, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)


class SkillListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == User.Role.MANAGER or request.user.role == User.Role.ADMIN:
            skills = Skill.objects.all()
            serializer = SkillSerializer(skills, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
        
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def create_task(request):
    user = request.user
    data = json.loads(request.body)
    try:
        project = Project.objects.get(id=data.project)
        assigned_to = ProjectTeamMember.objects.get(id=data.assigned_to)
        print(project)
        ticket = Ticket(
            title=data.title,
            description=data.description,
            end_date=data.end_date,
            project=project,
            assigned_to=assigned_to
        )
        ticket.save()
        return JsonResponse({'message': 'Success'})
    except:
        return JsonResponse({'error': 'Something went wrong'})