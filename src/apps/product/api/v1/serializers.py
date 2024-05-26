from rest_framework import serializers

from apps.product.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_id', 'name', 'price', 'rating', 'average_score']
