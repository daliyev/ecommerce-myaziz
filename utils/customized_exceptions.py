# In your Django app's `views.py` or a separate `exceptions.py` file

from rest_framework.views import exception_handler
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, ObjectDoesNotExist):
        model = str(exc).split(" ")[0]
        response = {
            'error': f"{model} mavjud emas",
            'status_code': 404
        }

        return Response(response, status=404)

    return response
