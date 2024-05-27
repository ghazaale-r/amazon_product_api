from django.db import models

class TimeStampedModel(models.Model):
    """
    Abstract base class that provides self-updating "created_at" and "updated_at" fields.
    All models that require timestamping for creation and last modification should inherit from this class.
    
    Attributes:
        created_at (DateTimeField): Field that stores the datetime the record was created, automatically set to the current date and time when the record is first created.
        updated_at (DateTimeField): Field that stores the datetime the record was last updated, automatically set to the current date and time every time the record is saved.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        
class Product(TimeStampedModel):
    """
    Represents a product with attributes like ID, name, price, rating, and average score.
    """
    product_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.CharField(max_length=100)  # Change FloatField to CharField
    average_score = models.FloatField()

    def __str__(self):
        return f"{self.product_id} - {self.name}"
