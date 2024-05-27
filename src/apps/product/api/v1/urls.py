from django.urls import path

from .views import ProductDetailAPIView


app_name = 'product'

urlpatterns = [
    path('product/', ProductDetailAPIView.as_view(), name='product-detail'),
]
