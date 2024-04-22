from rest_framework import serializers

from ProductsApp.models import Product, ProductImage, Likes


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)

    class Meta:
        model = Product
        fields = (
            'id', 'phoneName', 'phoneMarka', 'cost', 'costType', 'phoneMemory', 'phoneColor', 'document', 'isNew',
            'comment', 'adress', 'phoneNumber', 'time', 'images', 'telegram')

    def save(self, **kwargs):
        images = self.validated_data.pop('images')
        product = Product.objects.create(user=self.context['request'].user, **self.validated_data)
        for image in images:
            ProductImage.objects.create(product=product, image=image)
        return product


class ProductGetSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        if self.context.get('one', None):
            image_query = obj.images.all()
            image = ImageSerializer(image_query, many=True)
            return image.data
        image_query = obj.images.first()
        image = ImageSerializer(image_query)
        return image.data

    class Meta:
        model = Product
        fields = (
            'id', 'user', 'phoneName', 'phoneMarka', 'cost', 'costType', 'phoneMemory', 'phoneColor', 'document',
            'isNew', 'comment', 'adress', 'phoneNumber', 'time', 'images', 'telegram')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context['request']
        if request.user.is_authenticated:
            like = Likes.objects.filter(user=request.user, product=instance).first()
            is_cart = Product.objects.filter(storedBy=request.user, id=instance.id).first()
            if is_cart:
                representation['isCart'] = True
            else:
                representation['isCart'] = False
            if like:
                representation['liked_status'] = True
            else:
                representation['liked_status'] = False

        return representation


class LikedProductSerializer(serializers.ModelSerializer):
    product = ProductGetSerializer()

    class Meta:
        model = Likes
        fields = ['product']


class IdSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class ImageDeleteSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    image_id = serializers.IntegerField()


class ConfirmOrRejectSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    action = serializers.BooleanField()