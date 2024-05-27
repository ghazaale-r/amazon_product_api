from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Product model.
    """
    list_display = ('product_id', 'name', 'price', 'rating', 'average_score', 'created_at', 'last_updated', 'edit_button')
    search_fields = ('product_id', 'name')
    list_filter = ('rating', 'average_score')
    ordering = ('-created_at',)

    def edit_button(self, obj):
        """
        Generate an edit button for each row in the list view.
        """
        url = reverse('admin:app_product_change', args=[obj.pk])
        return format_html('<a href="{}">Edit</a>', url)
    
    edit_button.short_description = 'Edit'
    
admin.site.register(Product, ProductAdmin)
