from ProductsApp.models import Product


def one_product(**kwargs):
    return Product.objects.get(**kwargs)
