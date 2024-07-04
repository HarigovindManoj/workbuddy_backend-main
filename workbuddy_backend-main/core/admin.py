from django.contrib import admin
from .models import Project, ProjectTeamMember, Ticket, Task, Comment

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'start_date', 'status')

class ProjectTeamMembersAdmin(admin.ModelAdmin):
    list_display = ('employee', 'project', 'joined_at')

# admin.site.register(Message)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectTeamMember, ProjectTeamMembersAdmin)
admin.site.register(Ticket)
admin.site.register(Task)
admin.site.register(Comment)