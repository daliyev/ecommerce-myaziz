from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import viewsets

from ProductsApp.models import Product
from UsersApp.models import UserVerification

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'phone_number', 'father_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'write_only': True},
        }

    def update(self, instance, validated_data):
        instance.set_password(validated_data.pop('password'))
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

    def save(self, **kwargs):
        try:
            phone_number1 = self.validated_data.get('username', None)
            password = self.validated_data['password']

            if phone_number1 and User.objects.filter(phone_number=phone_number1).exists():
                raise ValidationError(detail="Bu telefon raqam ro'yhatdan o'tgan")

            User.objects.create_user(username=phone_number1, phone_number=phone_number1, password=password)
            return Response("User created successfully", status=201)
        except IntegrityError as e:
            return Response({"error": str(e)}, status=400)


class UserLikeSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

    def save(self, **kwargs):
        product = Product.objects.filter(id=self.validated_data["product_id"]).first()
        if product is None:
            raise ValidationError(detail="Bunday product mavjud emas")
        if self.context['request'].user.likedProducts.filter(id=self.validated_data["product_id"]):
            raise ValidationError(detail="Bu sizni savatingizda mavjud")
        self.context['request'].user.likedProducts.add(product)
        return product


class UserBucketSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

    def save(self, **kwargs):
        product = Product.objects.filter(id=self.validated_data["product_id"]).first()
        if product is None:
            raise ValidationError(detail="Bunday product mavjud emas")
        if self.context['request'].user.likedProducts.filter(id=self.validated_data["product_id"]):
            raise ValidationError(detail="Bu sizni savatingizda mavjud")
        self.context['request'].user.bucket.add(product)
        return product


class UserVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVerification
        fields = ['username', 'password', 'smsCode']


class RecoverPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.IntegerField(required=False)


class SetRecoveryPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.IntegerField()
    password = serializers.CharField()


class GoogleTokenSerializer(serializers.Serializer):
    token = serializers.CharField()

