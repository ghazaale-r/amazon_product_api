from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator, RegexValidator

from django_filters import rest_framework as filters

from apps.product.models import Product

# ASIN is a keyword used by Amazon for its product_ids
def validate_asin(value):
    # "A-Z" "0-9"
    if not value.isalnum() or not value.isupper():
        raise ValidationError("Invalid product_id ")

class ProductFilter(filters.FilterSet):
    product_id = filters.CharFilter(
        field_name="product_id", 
        required=True, 
        validators=[
            MaxLengthValidator(10), 
            MinLengthValidator(10),
            validate_asin
        ]
    )
    class Meta:
        model = Product
        fields = []