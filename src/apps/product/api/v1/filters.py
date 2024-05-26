from django_filters import rest_framework as filters

from apps.product.models import Product


class ProductFilter(filters.FilterSet):
    product_id = filters.CharFilter(field_name="product_id", required=True)

    class Meta:
        model = Product
        fields = []