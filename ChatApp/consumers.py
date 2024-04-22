import json
from django.core.exceptions import ObjectDoesNotExist
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenBackendError, TokenError
from rest_framework.exceptions import AuthenticationFailed
users = {}


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print(self)
        try:
            token = self.scope['query_string'].decode().split('=')[1]
            decoded_token = AccessToken(token)
            await self.accept()
            users[decoded_token['user_id']] = self.channel_name
            self.scope['user_id'] = decoded_token['user_id']
            await self.send(text_data=json.dumps({'message': 'hello'}))
        except TokenError as e:
            print('bu token da muammo bor', e)
            # raise AuthenticationFailed("Tokenda muammo bor")
        # print(self.scope['user'].is_authenticated)
        # print(self.channel_name)
        # await self.channel_layer.add
        # if self.scope['user'].is_anonymous:
        #     await self.close()
        # else:
        #     await self.accept()

    async def disconnect(self, code):
        try:
            del users[self.scope['user_id']]
        except:
            pass

    # async def receive_json(self, content, **kwargs):
    #     await self.send_json(content)
    # async def receive(self, text_data=None, bytes_data=None, **kwargs):
    #     text_data_get = json.loads(text_data)
    #     await self.send_json(text_data_get['message'])

    async def private_chat(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({"message": message}))
