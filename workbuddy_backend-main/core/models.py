from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _

from django.contrib.auth import get_user_model
from users.models import Manager, Employee

from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from django.dispatch import receiver
from asgiref.sync import async_to_sync
import json

from django.utils import timezone

User = get_user_model()

class StatusChoices(models.TextChoices):
        WORKING = 'W', _('Working')
        PENDING = 'P', _('Pending')
        COMPLETED = 'C', _('Completed')
    
class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    completion = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=1,
        choices=StatusChoices.choices,
        default=StatusChoices.WORKING
    )
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='projects')

    def __str__(self):
        return self.name

class ProjectTeamMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='project_team_members')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_team_members')

    class Meta:
        unique_together = ('employee', 'project')

    def __str__(self):
        return self.employee.email

class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=225)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    completion = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=1,
        choices=StatusChoices.choices,
        default=StatusChoices.WORKING
    )
    assigned_to = models.ForeignKey(ProjectTeamMember, on_delete=models.CASCADE, related_name='tickets')

    def __str__(self):
        return self.title
    
    @staticmethod
    def get_project_tickets(project_id, assigned_to=None):
        tickets = Ticket.objects.filter(assigned_to__project__id=project_id)
        if assigned_to:
            tickets = tickets.filter(assigned_to__employee=assigned_to)
        data = []
        for ticket in tickets:
            if ticket.end_date < timezone.now() and ticket.status != 'P':
                ticket.status = 'P'
                ticket.save(update_fields=['status']) 
                
            ticket_data = {
                'id': str(ticket.id),
                'title': ticket.title,
                'description': ticket.description,
                'end_date': str(ticket.end_date),
                'status': ticket.status,
                'assigned_to': str(ticket.assigned_to)
            }
            data.append(ticket_data)
        return data
    
    def delete(self, *args, **kwargs):
        channel_layer = get_channel_layer()
        data = {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'end_date': str(self.end_date),
            'status': self.status,
            'assigned_to': str(self.assigned_to.id)
        }
        async_to_sync(channel_layer.group_send)(
            'ticket_%s' % str(self.assigned_to.project.id),
            {
                'type': 'ticket_deleted',
                'value': json.dumps(data)
            }
        )
        
        super().delete(*args, **kwargs)


class Task(models.Model):   
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=225)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    completion = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=1,
        choices=StatusChoices.choices,
        default=StatusChoices.WORKING
    )
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(ProjectTeamMember, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, blank=True, null=True, related_name='comments')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=True, null=True, related_name='comments')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
    
@receiver(post_save, sender=Ticket)
def ticket_status_handler(sender, instance, created, **kwargs):
    # if not created:

    channel_layer = get_channel_layer()
    data = {
        'id': str(instance.id),
        'title': instance.title,
        'description': instance.description,
        'end_date': str(instance.end_date),
        'status': instance.status,
        'assigned_to': str(instance.assigned_to.id)
    }
    async_to_sync(channel_layer.group_send)(
        'ticket_%s' % str(instance.assigned_to.project.id),
        {
            'type': 'ticket_status',
            'value': json.dumps(data)
        }
    )