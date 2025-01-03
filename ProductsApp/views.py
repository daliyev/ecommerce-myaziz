import json
import os
from time import sleep
from django.db.models import Q
from django.contrib.auth.models import User
import requests
from django.http import JsonResponse
from rest_framework.decorators import action, api_view
from rest_framework.pagination import CursorPagination, PageNumberPagination, LimitOffsetPagination

from utils.imports import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product, Views, Likes, ProductImage, AppFile
from .serializers import AppFileSerializer, ProductSerializer, ImageSerializer, ProductGetSerializer, IdSerializer, ImageDeleteSerializer, \
    ConfirmOrRejectSerializer
from .functions import one_product

bot_token = os.getenv('bot_token')
chat_id = os.getenv('chat_id')
marketing_token = os.getenv('marketing_token')


def get_product(product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise CustomException(detail=none)

    return product


# class ProductApi(APIView):
#     serializer_class = ProductSerializer
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         serializer = ProductSerializer(data=request.data, context={"request": request})
#         if serializer.is_valid():
#             product = serializer.save()
#             images = ProductImage.objects.filter(product=product).all()
#             document = "Bor" if serializer.data['document'] else "Yo'q"
#             new = "Yangi" if serializer.data['isNew'] else "Foydalanilgan"
#             caption = f"ID: {product.id}\n\n📱Nomi: {serializer.data['phoneName']}\n📍Model: {serializer.data['phoneMarka']}\n💰Narxi: {serializer.data['cost']} {serializer.data['costType']}\n💾Xotirasi: {serializer.data['phoneMemory']}\n🎨Rangi: {serializer.data['phoneColor']}\n📦Dokument: {document}\n⚙️Xolati: {new}\n🛠Qo'shimcha: {serializer.data['comment']}\n📌Manzil: {serializer.data['adress']}\n✉️Telegram: {serializer.data['telegram']}"
#             url = f'https://api.telegram.org/bot{marketing_token}/sendMediaGroup'
#             url2 = f'https://api.telegram.org/bot{marketing_token}/sendMessage'
#             inline_keyboard = {
#                 'inline_keyboard': [
#                     [
#                         {'text': 'Tasdiqlash', 'callback_data': f"prconfirm_{product.id}"},
#                         {'text': 'Qaytarish', 'callback_data': f"prreject_{product.id}"}
#                     ]
#                 ]
#             }
#             media = []
#             for image in images:
#                 media.append({'type': 'photo', 'media': f"https://telmee.4fun.uz/media/{image.image}"})
#             media[-1]['caption'] = caption
#             reply_markup = json.dumps(inline_keyboard)
#             data = {
#                 'chat_id': chat_id,
#                 'media': media,
#             }
#             data2 = {
#                 'chat_id': chat_id,
#                 'text': f"Yangi elon joylandi(id:{product.id})",
#                 'reply_markup': reply_markup
#             }
#
#             requests.post(url, json=data)
#             requests.post(url2, data2)
#             print(Response.status_code)
#             return Response(data=success, status=201)
#         return Response(data=serializer.errors, status=400)
#
#     def get(self, request):
#         products = request.user.product.all()
#         serializer = ProductGetSerializer(products, many=True, context={"request": request})
#         return Response(data=serializer.data, status=200)
#
#     def put(self, request):
#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             product = request.user.product.filter(id=request.data['id']).first()
#             if not product:
#                 raise CustomException(restricted)
#             product.__dict__.update(**serializer.validated_data)
#             product.save()
#             return Response(success, 200)
#         return Response(serializer.errors, 400)
#
#     def delete(self, request):
#         product_id = request.query_params.get('id', None)
#         if product_id:
#             product = Product.objects.filter(id=product_id).first()
#             if product:
#                 product.delete()
#                 return Response(data=success, status=200)
#             return Response(data=none, status=400)
#         return Response(data=value_e, status=400)


class ProductFilterApi(APIView):
    def get(self, request):
        products = Product.objects
        name = request.query_params.get('name', None)
        location = request.query_params.get('location', None)
        condition = request.query_params.get('condition', None)
        model = request.query_params.get('model', None)
        currency = request.query_params.get('currency', None)
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)
        if name:
            products = products.filter(phoneName__icontains=name)
        if location:
            products = products.filter(adress__icontains=location)
        if condition:
            if condition == "NEW":
                products = products.filter(isNew=True)
            else:
                products = products.filter(isNew=False)
        if model:
            products = products.filter(phoneMarka__icontains=model)
        if currency:
            products = products.filter(costType=currency)
        if min_price:
            products = products.filter(cost__gte=min_price)
        if max_price:
            products = products.filter(cost__lte=max_price)
        products = products.all().order_by("?")

        serializer = ProductGetSerializer(products, many=True, context={"request": request})
        return Response(data=serializer.data, status=200)


# class ProductFilterApi(APIView):
#     def get(self, request):
#         products = Product.objects
#         name = request.query_params.get('name', None)
#         location = request.query_params.get('location', None)
#         condition = request.query_params.get('condition', None)
#         model = request.query_params.get('model', None)
#         currency = request.query_params.get('currency', None)
#         min_price = request.query_params.get('min_price', None)
#         max_price = request.query_params.get('max_price', None)
#         if name:
#             products = products.filter(phoneName__icontains=name)
#         if location:
#             products = products.filter(adress__icontains=location)
#         if condition:
#             if condition == "NEW":
#                 products = products.filter(isNew=True)
#             else:
#                 products = products.filter(isNew=False)
#         if model:
#             products = products.filter(phoneMarka__icontains=model)
#         if currency:
#             products = products.filter(costType=currency)
#         if min_price:
#             products = products.filter(cost__gte=min_price)
#         if max_price:
#             products = products.filter(cost__lte=max_price)
#         products = products.all().order_by("?")
#
#         vip_users = User.objects.filter(is_superuser=True).values('id').exclude(username__in=['admin'])
#         vip_users_products = products.filter(user__in=vip_users).order_by('-time')
#         vip_user_products_serializer = ProductGetSerializer(vip_users_products, many=True, context={'request': request})
#         products = products.exclude(id__in=vip_users_products)
#         product_serializer = ProductGetSerializer(products, many=True, context={"request": request})
#         return Response({
#             'vip_user_products': vip_user_products_serializer.data,
#             'products': product_serializer.data
#         }, status=200)


class ProductApi(APIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            product = serializer.save()
            images = ProductImage.objects.filter(product=product).all()
            document = "Bor" if serializer.data['document'] else "Yo'q"
            new = "Yangi" if serializer.data['isNew'] else "Foydalanilgan"
            caption = f"ID: {product.id}\n\n📱Nomi: {serializer.data['phoneName']}\n📍Model: {serializer.data['phoneMarka']}\n💰Narxi: {serializer.data['cost']} {serializer.data['costType']}\n💾Xotirasi: {serializer.data['phoneMemory']}\n🎨Rangi: {serializer.data['phoneColor']}\n📦Dokument: {document}\n⚙️Xolati: {new}\n🛠Qo'shimcha: {serializer.data['comment']}\n📌Manzil: {serializer.data['adress']}\n✉️Telegram: {serializer.data['telegram']}"
            url = f'https://api.telegram.org/bot{marketing_token}/sendMediaGroup'
            url2 = f'https://api.telegram.org/bot{marketing_token}/sendMessage'
            inline_keyboard = {
                'inline_keyboard': [
                    [
                        {'text': 'Tasdiqlash', 'callback_data': f"prconfirm_{product.id}"},
                        {'text': 'Qaytarish', 'callback_data': f"prreject_{product.id}"}
                    ]
                ]
            }
            media = []
            for image in images:
                media.append({'type': 'photo', 'media': f"https://telmee.4fun.uz/media/{image.image}"})
            media[-1]['caption'] = caption
            reply_markup = json.dumps(inline_keyboard)
            data = {
                'chat_id': chat_id,
                'media': media,
            }
            data2 = {
                'chat_id': chat_id,
                'text': f"Yangi elon joylandi(id:{product.id})",
                'reply_markup': reply_markup
            }

            requests.post(url, json=data)
            requests.post(url2, data2)
            return Response(data=success, status=201)
        return Response(data=serializer.errors, status=400)

    def get(self, request):
        products = request.user.product.all()
        serializer = ProductGetSerializer(products, many=True, context={"request": request})
        return Response(data=serializer.data, status=200)

    def put(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = request.user.product.filter(id=request.data['id']).first()
            if not product:
                raise CustomException(restricted)
            product.__dict__.update(**serializer.validated_data)
            product.save()
            return Response(success, 200)
        return Response(serializer.errors, 400)

    def delete(self, request):
        product_id = request.query_params.get('id', None)
        if product_id:
            product = Product.objects.filter(id=product_id).first()
            if product:
                product.delete()
                return Response(data=success, status=200)
            return Response(data=none, status=400)
        return Response(data=value_e, status=400)


class ProductAllApi(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductGetSerializer(products, many=True, context={"request": request})
        return Response(serializer.data, status=200)


@api_view(['GET'])
def retrieve(request):
    pk = request.query_params.get("id", None)
    if pk:
        print("product_id: ", pk)
        product = Product.objects.filter(id=pk).first()
        print("product: ", product)
        serializer = ProductGetSerializer(product, context={"request": request, 'one': True})

        if product is None:
            raise ValueError("Product does not exist.")

        related_products = Product.objects.filter(Q(phoneMarka=product.phoneMarka) | Q(adress=product.adress)).exclude(id=product.id)[:15]
        related_serializer = ProductGetSerializer(related_products, many=True, context={"request": request})
        other_products_by_user = Product.objects.filter(user=product.user).exclude(id=product.id)[:5]
        user_related_serializer = ProductGetSerializer(other_products_by_user, many=True, context={"request": request})
        if request.user.is_authenticated:
            view = Views.objects.filter(user=request.user, product=product).first()
            like = Likes.objects.filter(user=request.user, product=product).first()
            data = serializer.data
            if not view:
                Views.objects.create(user=request.user, product=product)
            if like:
                likes_count = product.liked.count()
                data['likes'] = likes_count
            views_count = product.views.count()
            data['views'] = views_count

            return Response({
                'product': data,
                'other_products_by_user': user_related_serializer.data,
                'related_products': related_serializer.data,
            }, status=200)
        return Response({
            'product': serializer.data,
            'other_products_by_user': user_related_serializer.data,
            'related_products': related_serializer.data,
        }, status=200)
    return Response("Product not exist.", 400)


class OneProductApi(APIView):
    def get(self, request):
        product_id = request.query_params.get("id", None)
        product = Product.objects.filter(id=product_id).first()
        serializer = ProductGetSerializer(product, context={"request": request, 'one': True})
        if request.user.is_authenticated:
            view = Views.objects.filter(user=request.user, product=product).first()
            like = Likes.objects.filter(user=request.user, product=product).first()
            data = serializer.data
            if not view:
                Views.objects.create(user=request.user, product=product)
            if like:
                likes_count = product.liked.count()
                data['likes'] = likes_count
            views_count = product.views.count()
            data['views'] = views_count

            return Response(data=data, status=200)
        return Response(serializer.data, status=200)


class AddLike(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = IdSerializer

    def get(self, request):
        product_ids = request.user.liked_products.values_list('product', flat=True)
        products = Product.objects.filter(id__in=product_ids).all()
        serializer = ProductGetSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, 200)

    def post(self, request):
        serializer = IdSerializer(data=request.data)
        if serializer.is_valid():
            product = get_product(serializer.validated_data['id'])
            like = Likes.objects.filter(user=request.user, product=product).first()
            if like:
                like.delete()
                return Response(success, 200)
            Likes.objects.create(user=request.user, product=product)
            return Response(success, 200)
        return Response(serializer.errors)


class ImageApi(APIView):
    serializer_class = IdSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ImageSerializer(data=request.data)

        if serializer.is_valid():
            if serializer.validated_data['product'].user != request.user:
                raise CustomException("Bu product sizga tegishli emas")
            ProductImage.objects.create(**serializer.validated_data)
            return Response(success, 200)
        raise CustomException(serializer.errors)

    def delete(self, request):
        serializer = ImageDeleteSerializer(data=request.data)
        if serializer.is_valid():
            product = request.user.product.filter(id=serializer.validated_data['product_id']).first()
            if not product:
                raise CustomException("Bu product sizga tegishli emas")
            product_image = ProductImage.objects.filter(id=serializer.validated_data['image_id']).first()
            if product_image:
                product_image.delete()
                return Response(success, 200)
            raise CustomException(none)
        raise CustomException(str(serializer.errors))


class MyCursorPagination(PageNumberPagination):
    page_size = 10  # Number of items per page
    ordering = '-time'  # Ordering by datetime, you can adjust this based on your model
    cursor_query_param = 'cursor'


class CustomOffSetPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 500


def paginate(instances, serializator, request):
    paginator = CustomOffSetPagination()
    paginated_order = paginator.paginate_queryset(instances, request)

    serializer = serializator(paginated_order, many=True, context={'request': request})

    return paginator.get_paginated_response(serializer.data)


class GetRecentProductApi(APIView):
    def get(self, request):
        products = Product.objects.all().order_by('-time')
        return paginate(products, ProductGetSerializer, request)


@api_view(['GET'])
def get_vip_user_products(request):
    vip_users = User.objects.filter(is_superuser=True).values('id').exclude(username__in=['admin'])
    print(">>vip users: ", vip_users)
    vip_users_products = Product.objects.filter(user__in=vip_users).order_by('-time')
    print(">>vip users product: ", vip_users_products)
    vip_users_products_serializer = ProductGetSerializer(vip_users_products, many=True, context={'request': request})
    return Response(vip_users_products_serializer.data, status=200)


class ConfirmOrRejectApi(APIView):
    # permission_27
    serializer_class = ConfirmOrRejectSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request):

        if not request.user.is_superuser:
            raise CustomException(restricted)

        serializer = ConfirmOrRejectSerializer(data=request.data)
        if serializer.is_valid():
            action = serializer.validated_data['action']
            product_id = serializer.validated_data['product_id']
            if action:

                product = Product.objects.get(id=product_id)
                if product.user.phone_number == "998900104240":
                    Product.objects.filter(id=product_id).update(status=4)
                    return Response(success, 200)
                Product.objects.filter(id=product_id).update(status=2)
                return Response(success, 200)

            Product.objects.filter(id=product_id).update(status=3)
            return Response(success, 200)
        return CustomException(serializer.errors)


class FileDownloadApi(APIView):
    serializer_class = AppFileSerializer

    def get(self, request):
        latest_file = AppFile.objects.latest('created_at')
        serializer = AppFileSerializer(latest_file,  context={'request': request})
        return Response(serializer.data, 200)

