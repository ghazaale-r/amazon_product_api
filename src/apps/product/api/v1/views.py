from django.core.cache import cache  # Import cache for caching functionality

# Import necessary modules from Django REST framework and other libraries
from rest_framework import generics
from rest_framework import generics, status
from rest_framework.response import Response  # Import Response for creating HTTP responses
from django_filters import rest_framework as filters

# Import necessary models and serializers from the application
from apps.product.models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter

# Import necessary modules for web scraping
import requests  # Import requests for making HTTP requests
from bs4 import BeautifulSoup  # Import BeautifulSoup for parsing HTML
from selenium import webdriver  
from selenium.webdriver.chrome.service import Service as ChromeService  
from selenium.webdriver.chrome.options import Options  # Import Options for configuring Chrome options
from webdriver_manager.chrome import ChromeDriverManager



# class ProductDetailAPIView(generics.ListAPIView):
class ProductDetailAPIView(generics.RetrieveAPIView):
    # Set the queryset and serializer class for the view
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # filter_backends = (filters.DjangoFilterBackend,) setted in settings.py in rest framwork settings section 
    filterset_class = ProductFilter

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve product details.
        """
        # Since the get method is overridden, we manually apply filters to ensure that the filtering logic is preserved.
        filtered_queryset = self.filter_queryset(self.get_queryset())
        
        # Get the product_id from query parameters
        product_id = request.query_params.get('product_id')
        # if not product_id:
        #     return self.error_response("Product ID is required", status.HTTP_400_BAD_REQUEST)

        # Check if product exists in cache
        product_data = self.check_cache(product_id)
        if product_data:
            return self.success_response(product_data, status.HTTP_200_OK)

        # Check if product exists in the database
        product_data = self.check_database(product_id)
        
        if product_data:
            cache.set(f"product_{product_id}", serializer.data, timeout=60*60*12) #  Cache for 12 hours
            return self.success_response(product_data, status.HTTP_200_OK)

        # Scrape product details from Amazon
        product_data = self.scrape_amazon_product_with_selenium(product_id)
        
        if product_data:
            
            # Check if all items except product_id are None
            if all(value is None for key, value in product_data.items() if key != 'product_id'):
                return self.error_response("Product data is incomplete", status.HTTP_400_BAD_REQUEST)
            
            # Save the product to the database
            product = Product(**product_data)
            product.save()
            serializer = ProductSerializer(product)
            cache.set(f"product_{product_id}", serializer.data, timeout=60*60*12)  # Cache for 12 hours
            return self.success_response(serializer.data, status.HTTP_201_CREATED)
        else:
            return self.error_response("Product not found", status.HTTP_404_NOT_FOUND)

    def check_cache(self, product_id):
        """
        Check if the product exists in the cache.
        """
        cache_key = f"product_{product_id}"
        return cache.get(cache_key)

    def check_database(self, product_id):
        """
        Check if the product exists in the database.
        """
        try:
            product = Product.objects.get(product_id=product_id)
            serializer = ProductSerializer(product)
            cache.set(f"product_{product_id}", serializer.data, timeout=60*15)  # Cache for 15 minutes
            return serializer.data
        except Product.DoesNotExist:
            return None

    def scrape_amazon_product_with_selenium(self, product_id):
        """
        Scrape product details from Amazon using Selenium.
        """
        url = f"https://www.amazon.com/dp/{product_id}"
        options = Options()
        options.headless = True  # Run Chrome in headless mode
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        
        try:
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            res = self.parse_soup(soup, product_id)
            return res
        
        finally:
            driver.quit()

    def parse_soup(self, soup, product_id):
        # Get the product title
            # example : <span id="productTitle" class="a-size-large product-title-word-break">        
            # OtterBox iPhone 15 Pro MAX (Only) Commuter Series Case - CRISP DENIM (Blue), slim &amp; tough, 
            # pocket-friendly, with port protection       
            # </span> 
        title_tag = soup.find('span', id='productTitle', class_='a-size-large product-title-word-break')
        name = title_tag.get_text(strip=True) if title_tag else None
        
        # Get the product price
        # <input type="hidden" id="twister-plus-price-data-price" value="38.54" />
        price_tag = soup.find('input', id='twister-plus-price-data-price')
        price = price_tag['value'] if price_tag and 'value' in price_tag.attrs else None

        # Get the product rating
        # <span id="acrCustomerReviewText" class="a-size-base">354 ratings</span>
        rating_tag = soup.find('span', id='acrCustomerReviewText', class_='a-size-base')
        rating = rating_tag.get_text(strip=True).split()[0] if rating_tag else None

        # Get the product average score
        # <span id="acrPopover" class="reviewCountTextLinkedHistogram noUnderline" title="4.6 out of 5 stars">
        average_score_tag = soup.find('span', id='acrPopover', class_='reviewCountTextLinkedHistogram noUnderline')
        average_score = average_score_tag['title'].split()[0] if average_score_tag and 'title' in average_score_tag.attrs else None
        
        return {
            "product_id": product_id,
            "name": name,
            "price": price,
            "rating": rating,
            "average_score": average_score
        }
        
    def success_response(self, data, status_code):
        """
        Create a standardized success response.
        """
        return Response({
            "status": "success",
            "data": data
        }, status=status_code)

    def error_response(self, message, status_code):
        """
        Create a standardized error response.
        """
        return Response({
            "status": "error",
            "message": message
        }, status=status_code)