from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework.exceptions import APIException
User = get_user_model()
success = "Amaliyot muvaffaqiyatli bajarildi"
error = "Xatolik yuz berdi"
none = "Kiritilganlar bo'yicha malumot topilmadi"
value_e = "Malumotlarni to'g'ri shakilda jo'nating"
restricted = "Bu amaliyot sizga ruhsat etilmagan"


class CustomException(APIException):
    status_code = 400
    default_detail = "Something went wrong"


