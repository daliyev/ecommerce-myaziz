import os
from datetime import timedelta
from random import randint

import requests
from django.db import transaction
from django.utils import timezone
from google.auth.transport import requests as r
from google.oauth2 import id_token
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from ProductsApp.serializers import ProductGetSerializer
from utils.imports import *
from .models import UserVerification, Recovery
from .serializers import UserSerializer, RegisterSerializer, UserLikeSerializer, UserBucketSerializer, \
    UserVerificationSerializer, RecoverPasswordSerializer, SetRecoveryPasswordSerializer, GoogleTokenSerializer

CLIENT_ID = os.getenv('CLIENT_ID')
sms_token = ""


def refresh_token():
    global sms_token
    url = "https://notify.eskiz.uz/api/auth/login"
    payload = {'email': 'izzatullaev2001abror@gmail.com',
               'password': 'Z7YaqztTs7NXs57IsYgVCdb0U2VfB0HyuhbD2rD4'}
    response = requests.request("POST", url, data=payload)
    if response.status_code == 200:
        sms_token = response.json()['data']['token']
        return sms_token


class RegisterApi(APIView):

    serializer_class = RegisterSerializer

    @transaction.atomic()
    def post(self, request):
        global sms_token
        code = randint(123467, 987654)
        request.data['smsCode'] = code
        serializer = UserVerificationSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['username']
            user = User.objects.filter(phone_number=phone_number).first()

            if user:
                raise CustomException("Bu telefon raqam foydalanilgan")

            user_fake = UserVerification.objects.filter(**request.data).last()
            if user_fake:
                if timezone.now() - user.datetime > timedelta(minutes=720):
                    return Response({'error': "Eski kodingiz hali ham kuchda"}, 409)
            url2 = "https://notify.eskiz.uz/api/message/sms/send"
            headers = {
                'Authorization': f'Bearer {sms_token}'
            }
            message = f"Telmee sayti uchun tasdiqlash ko'dingiz: {code}"
            payload = {'mobile_phone': phone_number,
                       'message': message,
                       'from': 'Telmee'}
            response = requests.post(url=url2, data=payload, headers=headers)
            if response.status_code != 200:
                sms_token = refresh_token()
                headers = {
                    'Authorization': f'Bearer {sms_token}'
                }
                response = requests.post(url=url2, data=payload, headers=headers)
            if response.status_code == 200:
                serializer.save()
                return Response(data={"Tasdiqlash code jonatildi"}, status=200)
            return Response(data=response, status=400)
        return Response(data=serializer.errors, status=400)


class UserVerificationApi(APIView):
    serializer_class = UserVerificationSerializer

    @transaction.atomic()
    def post(self, request):
        user = UserVerification.objects.filter(**request.data).last()
        if user:
            if timezone.now() - user.datetime > timedelta(minutes=720):
                UserVerification.objects.filter(**request.data).delete()
                return Response(data="Sms code amal qilish muddati tugadi", status=400)
            user = User.objects.create_user(username=user.username, phone_number=user.username, password=request.data['password'])
            refresh = RefreshToken.for_user(user)
            UserVerification.objects.filter(username=request.data['username'], password=request.data['password']).delete()
            data = {
                'message': "Foydalanuvchi muvaffaqiyatli yaratildi",
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
            return Response(data=data, status=200)
        return Response({'error': "Kiritilgan kod xato"}, status=400)


class RecoverPasswordApi(APIView):
    serializer_class = RecoverPasswordSerializer
    def post(self, request):
        global sms_token
        serializer = RecoverPasswordSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            user = User.objects.filter(phone_number=phone_number).first()
            if not user:
                raise CustomException("Siz ro'yxatdan o'tmagansiz")
            code = randint(123467, 987654)
            request.data['smsCode'] = code
            url2 = "https://notify.eskiz.uz/api/message/sms/send"
            headers = {
                'Authorization': f'Bearer {sms_token}'
            }
            message = f"Telmee sayti uchun parol tiklash uchun kodingiz: {code}"
            payload = {'mobile_phone': phone_number,
                       'message': message,
                       'from': 'Telmee'}
            response = requests.post(url=url2, data=payload, headers=headers)
            if response.status_code != 200:
                sms_token = refresh_token()
                headers = {
                    'Authorization': f'Bearer {sms_token}'
                }
                response = requests.post(url=url2, data=payload, headers=headers)
            if response.status_code == 200:
                Recovery.objects.create(phone_number=phone_number, code=code)
                return Response("Sms code muvaffaqiyatli yuborildi", 200)
            return Response(response, 400)

    def put(self, request):
        serializer = RecoverPasswordSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            code = serializer.validated_data.get('code', None)
            if code is None:
                raise CustomException("Code kiritilmagan")
            recover = Recovery.objects.filter(phone_number=phone_number, code=code).first()
            if recover:
                return Response(data="Foydalanuvchi parolni yangilash uchun tasdiqlandi", status=200)
            raise CustomException("Notog'ri ko'd kiritildi")
        raise CustomException(serializer.errors)


class SetRecoveryPasswordApi(APIView):
    serializer_class = SetRecoveryPasswordSerializer
    def post(self, request):
        serializer = SetRecoveryPasswordSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            code = serializer.validated_data['code']
            password = serializer.validated_data['password']
            recover = Recovery.objects.filter(phone_number=phone_number, code=code).first()
            if not recover:
                raise CustomException("Xatolik yuz berdi")
            user = User.objects.filter(username=phone_number).first()
            user.set_password(password)
            user.save()
            recover.delete()
            return Response(success, 200)
        raise CustomException(serializer.errors)


class UserApi(APIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=200)

    def put(self, request):
        data = request.data.copy()
        password = data.get('password', None)
        if password:
            request.user.set_password(password)
            data.pop('password')
        for attr, value in request.data.items():
            if value:
                if attr in ["username", 'email']:
                    pass
                else:
                    setattr(request.user, attr, value)

        request.user.save()
        return Response(data=success, status=200)


class LikeAddApi(APIView):
    serializer_class = UserLikeSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = request.user.likedProducts.all()
        serializer = ProductGetSerializer(data, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = UserLikeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(data=success, status=200)
        return Response(data=serializer.errors, status=400)

    def delete(self, request):
        product_id = request.data.get('product_id', None)
        if product_id:
            product = request.user.likedProducts.filter(id=product_id)
            if product:
                product.delete()
                return Response(data=success, status=200)
            return Response(data=none, status=400)
        return Response(data=value_e, status=400)


class BucketAddApi(APIView):
    serializer_class = UserBucketSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = request.user.bucket.all()
        serializer = ProductGetSerializer(data, many=True, context={'request': request})
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = UserBucketSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(data=success, status=200)
        return Response(data=serializer.errors, status=400)

    def delete(self, request):
        product_id = request.query_params.get('product_id', None)
        if product_id:
            product = request.user.bucket.filter(id=product_id).first()
            if product:
                request.user.bucket.remove(product.id)
                return Response(data=success, status=200)
            return Response(data=none, status=400)
        return Response(data=value_e, status=400)


class GoogleRegisterApi(APIView):
    serializer_class = GoogleTokenSerializer

    def post(self, request):
        serializer = GoogleTokenSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            try:
                idinfo = id_token.verify_oauth2_token(token, r.Request(), CLIENT_ID)
            except Exception as e:
                raise CustomException(error)
            email = idinfo['email']
            user = User.objects.filter(email=email).first()
            if not user:
                username = email.split('@')[0]
                user = User.objects.create_user(username=username, email=email, by_phone=False)
                refresh = RefreshToken.for_user(user)
                data = {
                    'message': "Foydalanuvchi muvaffaqiyatli yaratildi",
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
                return Response(data=data, status=200)

            refresh = RefreshToken.for_user(user)
            data = {
                'message': "Foydalanuvchi login qilindi",
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
            return Response(data=data, status=200)
        raise CustomException(serializer.errors)


class GoogleToPhoneApi(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GoogleTokenSerializer

    def post(self, request):
        serializer = GoogleTokenSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            try:
                idinfo = id_token.verify_oauth2_token(token, r.Request(), CLIENT_ID)
            except Exception as e:
                print(e)
                raise CustomException(error)
            email = idinfo['email']
            request.user.email = email
            request.user.save()
            return Response(success, 200)
        raise CustomException(serializer.errors)
