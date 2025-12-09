"""
URL configuration for ecommerce project.
"""
from django.contrib import admin
from django.urls import path
from store.views import *
from django.conf.urls.static import static
from django.conf import settings # Import settings for media files

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core Store Views
    path('', store, name='store'),
    
    # ⭐ NEW PATH ADDED FOR PRODUCT DETAIL ⭐
    # <int:pk>/ captures the product ID and passes it to the productDetail view
    path('product/<int:pk>/', productDetail, name='product_detail'),
    
    # Cart and Checkout Views
    path('cart/', cart, name='cart'),
    path('checkout/', checkout, name='checkout'),
    
    # AJAX Views
    # FIX: Added trailing slash (/) to match JavaScript fetch call
    path('update_item/', updateItem, name='update_item'),
    path('process_order/', processOrder, name="process_order")
]

# Serve media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)