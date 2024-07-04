from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('api/create-project/', views.ProjectCreationView.as_view(), name='create-project'),
    path('api/project-list/', views.ProjectListView.as_view(), name='project-list'),
    path('api/project-detail/<id>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('api/project-detail/<id>/project-team-members/', views.ProjectTeamMemberView.as_view(), name='project-team-members'),
    path('api/project-detail/<id>/add-tm/', views.AddTMView.as_view(), name='add-tm'),
    path('api/skill-list/', views.SkillListView.as_view(), name='skill-list'),

    path('api/create-task/', views.create_task, name='create-task'),
]