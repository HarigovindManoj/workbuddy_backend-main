import json

from channels.generic.websocket import WebsocketConsumer
from .models import Ticket, ProjectTeamMember, Project
from asgiref.sync import async_to_sync

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

class TicketConsumer(WebsocketConsumer):
    
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['project_id']
        self.room_group_name = 'ticket_%s' % self.room_name
        self.user = self.scope['user']
        self.is_manager = False
        self.is_project_tm = False

        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        
        project_tms = ProjectTeamMember.objects.filter(project__id=self.room_name)
        self.project_team_members = project_tms.values_list('employee__email', flat=True)
        if self.user.email in Project.objects.get(id=self.room_name).manager.email:
            self.is_manager = True
        if self.user.email in project_tms.values_list('employee__email', flat=True):
            self.is_project_tm = True

        if self.is_manager or self.is_project_tm:
            self.accept()

        if self.is_manager:
            tickets = Ticket.get_project_tickets(self.room_name)
        else:
            tickets = Ticket.get_project_tickets(self.room_name, assigned_to=self.user)
            
        self.send(
            text_data=json.dumps({
                'payload': tickets
            })
        )
    
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        if self.is_manager:
            data = json.loads(text_data)
            if data['method'] == 'DELETE':
                ticket = Ticket.objects.get(id=data['ticket_id'])
                ticket.delete()
            elif data['method'] == 'POST':
                new_ticket = Ticket(
                    title=data['title'],
                    description=data['description'],
                    end_date=data['end_date'],
                    assigned_to=ProjectTeamMember.objects.get(id=data['assigned_to']),
                )
                new_ticket.save()
        
        elif self.is_project_tm:
            data = json.loads(text_data)
            ticket_update = Ticket.objects.get(id=data['message'])
            project_tm = ProjectTeamMember.objects.get(employee__id=self.user.id)
            
            if ticket_update.assigned_to.id == project_tm.id and not ticket_update.status == 'C':
                ticket_update.status = 'C'
                ticket_update.completion = timezone.now()
                ticket_update.save()

        # async_to_sync(
        #     self.channel_layer.group_send)(
        #     self.room_group_name, {
        #         'type': 'ticket_status',
        #         'payload': tickets
        #     }
        # )

    def ticket_status(self, event):
        ticket = json.loads(event['value'])
        try:
            project_tm = ProjectTeamMember.objects.get(employee__id=self.user.id)
            if ticket['assigned_to'] == str(project_tm.id):
                tickets = Ticket.get_project_tickets(self.room_name, assigned_to=self.user)
                self.send(text_data=json.dumps({
                    'payload': tickets
                }))
            #     print('send to employee')
            # else:
            #     print('someothers')

        except ObjectDoesNotExist:
            if self.is_manager:
                tickets = Ticket.get_project_tickets(self.room_name)
                self.send(text_data=json.dumps({
                    'payload': tickets
                }))
                # print('send to manager')

    def ticket_deleted(self, event):
        ticket = json.loads(event['value'])
        try:
            project_tm = ProjectTeamMember.objects.get(employee__id=self.user.id)
            if ticket['assigned_to'] == str(project_tm.id):
                tickets = Ticket.get_project_tickets(self.room_name, assigned_to=self.user)
                self.send(text_data=json.dumps({
                    'payload': tickets
                }))
            #     print('send to employee')
            # else:
            #     print('someothers')

        except ObjectDoesNotExist:
            if self.is_manager:
                tickets = Ticket.get_project_tickets(self.room_name)
                self.send(text_data=json.dumps({
                    'payload': tickets
                }))
                # print('send to manager')