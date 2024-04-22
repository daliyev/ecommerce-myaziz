from rest_framework import serializers


class ChatSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    message = serializers.CharField()