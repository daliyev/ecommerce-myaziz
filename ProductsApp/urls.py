from django.urls import path
from .views import FileDownloadApi, ProductApi, ProductAllApi, AddLike, OneProductApi, ImageApi, ProductFilterApi, GetRecentProductApi, \
    ConfirmOrRejectApi, get_vip_user_products, retrieve

urlpatterns = [
    path('', ProductApi.as_view()),
    path('all/', ProductAllApi.as_view()),
    path('product_like/', AddLike.as_view()),
    path('one_product/', OneProductApi.as_view()),
    path('retrieve/', retrieve),
    path('image/', ImageApi.as_view()),
    path('search/', ProductFilterApi.as_view()),
    path('recent_products/', GetRecentProductApi.as_view()),
    path('vip_user_products/', get_vip_user_products),
    path('confirm_reject/', ConfirmOrRejectApi.as_view()),
    path('apk/', FileDownloadApi.as_view(), name="apk"),
]
