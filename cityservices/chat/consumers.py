import json
from django.contrib.auth.models import User
from bookings.models import Booking
from .models import Message
from channels.generic.websocket import WebsocketConsumer

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.target = User.objects.filter(id=self.scope['url_route']['kwargs']['user_id']).first()
        self.user = self.scope.get('user')
        if not self.user or not self.user.is_authenticated or not self.target or not Booking.objects.filter(user=self.user, service__provider=self.target).exists() and not Booking.objects.filter(user=self.target, service__provider=self.user).exists():
            self.close()
            return
        self.room_group_name = f'chat_{min(self.user.id, self.target.id)}_{max(self.user.id, self.target.id)}'
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        self.channel_layer = get_channel_layer()
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            from asgiref.sync import async_to_sync
            async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        record = Message.objects.create(sender=self.user, receiver=self.target, content=message)

        from asgiref.sync import async_to_sync
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, {'type': 'chat.message', 'message': record.content, 'sender': self.user.username})

    def chat_message(self, event):
        self.send(text_data=json.dumps({'message': event['message'], 'sender': event['sender']}))