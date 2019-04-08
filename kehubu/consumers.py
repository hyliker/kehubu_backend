import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer


class KehubuConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()
        user = self.scope.get('user')
        member_set = user.user_kehubu_member_set.all()
        for member in member_set:
            group_channel_name = member.group.channel_name
            async_to_sync(self.channel_layer.group_add)(group_channel_name, self.channel_name)

    def disconnect(self, close_code):
        user = self.scope.get('user')
        member_set = user.user_kehubu_member_set.all()
        for member in member_set:
            group_channel_name = member.group.channel_name
            async_to_sync(self.channel_layer.group_discard)(group_channel_name, self.channel_name)

    def receive_json(self, content):
        print("receive_json", content)

    def kehubu_member_add(self, content):
        print('kehubu_member_add', content)
        self.send_json(content)

    def kehubu_member_delete(self, content):
        print('kehubu_member_delete', content)
        self.send_json(content)
