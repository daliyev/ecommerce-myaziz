from utils.imports import *
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .consumers import users as user_websocket
from .serializers import ChatSerializer


class SendMessageApi(APIView):
    serializer_class = ChatSerializer

    def post(self, request):
        serializer = ChatSerializer(data=request.data)
        # if serializer.is_valid():
        #     channel_layer = get_channel_layer()
        #     reciver_id = serializer.validated_data.get('user_id', None)
        #     message = serializer.validated_data['message']
        #     websocket = user_websocket.get(reciver_id, None)
        #     # if websocket is None:
        #
        #
        #     async_to_sync(channel_layer.send)(, {'type': 'private_chat','message': message})
        #     return Response('great', 200)
        # return Response(serializer.errors, 400)
