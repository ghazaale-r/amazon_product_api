"""
این اولین راه حل من برای دور زدن کپچا ی آمازون بود 
از زمانیکه متوجه شدم هنگام دیدن صفحه از طریق برنامه صفحه ی کپچا را می اورد 
ولی موفقیت امیز نیود
زیرا برای گرفتن TWOCAPTCHA_API_KEY
باید پرداخت انجام میشد 
استفاده از ماژول 2captcha

"""

import os
import logging
from django.core.cache import cache  # Import cache for caching functionality

# Import necessary modules from Django REST framework and other libraries
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
from selenium.webdriver.chrome.options import Options  # Import Options for configuring Chrome options
from twocaptcha import TwoCaptcha  # Import TwoCaptcha for solving CAPTCHA


# logging settings store in file
log_file = 'scraper.log'
logging.basicConfig(level=logging.INFO, filename=log_file, filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



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

    def create_webdriver(self):
        selenium_host = os.getenv('SELENIUM_HOST', 'selenium')
        selenium_port = os.getenv('SELENIUM_PORT', '4444')
        selenium_url = f'http://{selenium_host}:{selenium_port}/wd/hub'

        options = Options()
        options.headless = True  # Run Chrome in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')

        driver = webdriver.Remote(
            command_executor=selenium_url,
            options=options
        )
        return driver
        
    def scrape_amazon_product_with_selenium(self, product_id):
        """
        Scrape product details from Amazon using Selenium.
        """
        url = f"https://www.amazon.com/dp/{product_id}"
        driver = self.create_webdriver()
        
        try:
            logger.info(f"Fetching URL: {url}")
            driver.get(url)
            
            page_source = driver.page_source
            captcha_form = '<form method="get" action="/errors/validateCaptcha"'
            if captcha_form in page_source or 'validatecaptcha' in page_source.lower or 'captcha' in page_source.lower():    
                logger.info("CAPTCHA detected. Solving CAPTCHA...")
                captcha_solution = self.solve_captcha(driver.page_source)
                if captcha_solution:
                    logger.info("Fetching URL again with CAPTCHA solution...")
                    driver.get(f"{url}&field-keywords={captcha_solution}")
                else:
                    logger.error("Failed to solve CAPTCHA.")
                    return None
                
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            res = self.parse_soup(soup, product_id)
            return res
        
        finally:
            driver.quit()

    def solve_captcha(self, page_source):
        """
        Solve CAPTCHA using 2Captcha service.
        """
        solver = TwoCaptcha(os.getenv('TWOCAPTCHA_API_KEY'))

        try:
            logger.info("Solving CAPTCHA...")
            result = solver.amazon(page_source)
            logger.info("CAPTCHA solved successfully.")
            return result['code']
        except Exception as e:
            logger.error(f"Failed to solve CAPTCHA: {e}")
            return None
        
    def parse_soup(self, soup, product_id):
        # Get the product title
            # example : <span id="productTitle" class="a-size-large product-title-word-break">        
            # OtterBox iPhone 15 Pro MAX (Only) Commuter Series Case - CRISP DENIM (Blue), slim &amp; tough, 
            # pocket-friendly, with port protection       
            # </span> 
        title_tag = soup.find('span', id='productTitle', class_='a-size-large product-title-word-break')
        if not title_tag:
            logger.error("No title_tag . Failed to fetch product page after CAPTCHA.")
            return None
        name = title_tag.get_text(strip=True) if title_tag else None
        
        # Get the product price
        # <input type="hidden" id="twister-plus-price-data-price" value="38.54" />
        price_tag = soup.find('input', id='twister-plus-price-data-price')
        if not price_tag:
            logger.error("No price_tag . Failed to fetch product page after CAPTCHA.")
            return None
        price = price_tag['value'] if price_tag and 'value' in price_tag.attrs else None

        # Get the product rating
        # <span id="acrCustomerReviewText" class="a-size-base">354 ratings</span>
        rating_tag = soup.find('span', id='acrCustomerReviewText', class_='a-size-base')
        if not rating_tag:
            logger.error("No rating_tag . Failed to fetch product page after CAPTCHA.")
            return None
        rating = rating_tag.get_text(strip=True).split()[0] if rating_tag else None

        # Get the product average score
        # <span id="acrPopover" class="reviewCountTextLinkedHistogram noUnderline" title="4.6 out of 5 stars">
        average_score_tag = soup.find('span', id='acrPopover', class_='reviewCountTextLinkedHistogram noUnderline')
        if not average_score_tag:
            logger.error("No average_score_tag . Failed to fetch product page after CAPTCHA.")
            return None
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