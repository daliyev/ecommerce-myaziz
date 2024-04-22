from django.urls import path

from .views import RegisterApi, LikeAddApi, UserApi, BucketAddApi, UserVerificationApi, RecoverPasswordApi, \
    SetRecoveryPasswordApi, GoogleRegisterApi, GoogleToPhoneApi

urlpatterns = [
    path('', UserApi.as_view(), name='user'),
    path('register/', RegisterApi.as_view(), name='register'),
    path('user_verification/', UserVerificationApi.as_view()),
    path('liked/', LikeAddApi.as_view(), name='toLiked'),
    path('bucket/', BucketAddApi.as_view(), name='bucket'),
    path('recovery/', RecoverPasswordApi.as_view()),
    path('set_password/', SetRecoveryPasswordApi.as_view()),
    path('google_register/', GoogleRegisterApi.as_view()),
    path('goole_to_phone/', GoogleToPhoneApi.as_view()),
]
