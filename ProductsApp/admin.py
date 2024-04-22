from django.contrib import admin
from .models import Product, ProductImage, Views, Likes
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Views)
admin.site.register(Likes)