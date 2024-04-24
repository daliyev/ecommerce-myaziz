from django.contrib import admin
from .models import AppFile, Product, ProductImage, Views, Likes
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Views)
admin.site.register(Likes)
admin.site.register(AppFile)