from django.urls import path
from .views import FileDownloadApi, ProductApi, ProductAllApi, AddLike, OneProductApi, ImageApi, ProductFilterApi, GetRecentProductApi, \
    ConfirmOrRejectApi

urlpatterns = [
    path('', ProductApi.as_view()),
    path('all/', ProductAllApi.as_view()),
    path('product_like/', AddLike.as_view()),
    path('one_product/', OneProductApi.as_view()),
    path('image/', ImageApi.as_view()),
    path('search/', ProductFilterApi.as_view()),
    path('recent_products/', GetRecentProductApi.as_view()),
    path('confirm_reject/', ConfirmOrRejectApi.as_view()),
    path('apk/', FileDownloadApi.as_view(), name="apk"),
]
