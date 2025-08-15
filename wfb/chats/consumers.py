# chat/consumers.py
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
# internals
from wfb.chats.models import Message


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message text from WebSocket
    def receive(self, text_data):
        res = json.loads(text_data)
        msg_obj = Message(text=res["text"],
                          job_id=res["job"],
                          sender_id=res["sender"],
                          receiver_id=res["receiver"],
                          chat_room_id=res["chat_room"],
                          )
        msg_obj.save()
        text = res["text"]

        # Send message text to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "text": text}
        )

    # Receive message text from room group
    def chat_message(self, event):
        text = event["text"]

        # Send message text to WebSocket
        self.send(text_data=json.dumps({"text": text}))
