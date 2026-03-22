from django.urls import path
from .views import (
    product_list_create,
    update_product,
    add_to_cart,
    view_cart,
    update_cart,
    delete_cart_item,
    place_order,
    view_orders,
    vendor_products,
    vendor_orders,
    update_order_status,
    vendor_dashboard,
    ai_search
)

urlpatterns = [

    # 🔹 Products
    path('products/', product_list_create),          # GET, POST
    path('products/<int:pk>/', update_product),      # PUT, PATCH

    # 🔹 Cart
    path('cart/', add_to_cart),                      # POST
    path('cart/view/', view_cart),                   # GET
    path('cart/<int:pk>/', update_cart),             # PATCH
    path('cart/delete/<int:pk>/', delete_cart_item), # DELETE

    # 🔹 Orders (Customer)
    path('orders/place/', place_order),              # POST
    path('orders/', view_orders),                    # GET

    # 🔹 Vendor
    path('vendor/products/', vendor_products),       # GET
    path('vendor/orders/', vendor_orders),           # GET
    path('vendor/dashboard/', vendor_dashboard),     # GET
    path('order/<int:pk>/status/', update_order_status),  # PATCH

    # 🔹 AI Search
    path('ai/search/', ai_search),                   # POST
]