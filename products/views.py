from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from .models import Product, Cart, Order, OrderItem
from .serializers import ProductSerializer, CartSerializer, OrderSerializer
import re
from django.db.models import Sum
from rest_framework.pagination import PageNumberPagination

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def product_list_create(request):

    if request.method == 'GET':
        user = request.user

        if user.role == "vendor":
            products = Product.objects.filter(vendor=user)
        else:
            products = Product.objects.all()

        paginator = PageNumberPagination()
        paginator.page_size = 5

        result = paginator.paginate_queryset(products, request)

        serializer = ProductSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    if request.method == 'POST':
        user = request.user

        if user.role not in ["vendor", "admin"]:
            return Response({"error": "Only vendors/admin can create products"}, status=403)

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(vendor=user)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_product(request, pk):
    user = request.user

    if user.role != "vendor":
        return Response({"error": "Only vendors allowed"}, status=403)

    product = get_object_or_404(Product, id=pk)

    if product.vendor != user:
        return Response({"error": "You can update only your products"}, status=403)

    serializer = ProductSerializer(product, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    user = request.user
    if request.user.role != "customer":
        return Response({"error": "Only customers allowed"}, status=403)
    product_id = request.data.get('product')
    quantity = int(request.data.get('quantity', 1))

    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=user,
        product=product
    )

    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()

    serializer = CartSerializer(cart_item)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    serializer = CartSerializer(cart_items, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    user = request.user

    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        return Response({"error": "Cart is empty"}, status=400)

    # ✅ Create Order
    order = Order.objects.create(user=user)

    # ✅ Create OrderItems
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity
        )

    # ✅ Clear Cart
    cart_items.delete()

    return Response({"message": "Order placed successfully"})



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_orders(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_cart(request, pk):
    if request.user.role != "customer":
        return Response({"error": "Only customers allowed"}, status=403)
    try:
        cart_item = Cart.objects.get(id=pk, user=request.user)
    except Cart.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    quantity = request.data.get('quantity')

    if quantity is not None:
        quantity = int(quantity)

        if quantity <= 0:
            cart_item.delete()
            return Response({"message": "Item removed"})
        else:
            cart_item.quantity = quantity
            cart_item.save()

    return Response({"message": "Cart updated"})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_cart_item(request, pk):
    
    if request.user.role != "customer":
        return Response({"error": "Only customers allowed"}, status=403)
    try:
        cart_item = Cart.objects.get(id=pk, user=request.user)
        cart_item.delete()
        return Response({"message": "Item deleted"})
    except Cart.DoesNotExist:
        return Response({"error": "Not found"}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vendor_products(request):
    products = Product.objects.filter(vendor=request.user)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vendor_orders(request):

    if request.user.role != "vendor":
        return Response({"error": "Not allowed"}, status=403)

    orders = Order.objects.filter(orderitem__product__vendor=request.user).distinct()

    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def ai_search(request):
    query = request.data.get('query', '').lower()
    # Extract price
    price_match = re.search(r'under (\d+)', query)
    max_price = int(price_match.group(1)) if price_match else None

    # 🔥 Remove price words from query
    cleaned_query = re.sub(r'under \d+', '', query).strip()

    # Filter products
    products = Product.objects.all()

    if cleaned_query:
        products = products.filter(name__icontains=cleaned_query)

    if max_price:
        products = products.filter(price__lte=max_price)

    products = products.order_by('price')

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, pk):
    if request.user.role != "vendor":
        return Response({"error": "Not allowed"}, status=403)
    try:
        order = Order.objects.get(id=pk)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    status = request.data.get('status')

    if status not in ["pending", "shipped", "delivered"]:
        return Response({"error": "Invalid status"}, status=400)
    
    order.status = status
    order.save()

    return Response({"message": "Order updated"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vendor_dashboard(request):

    if request.user.role != "vendor":
        return Response({"error": "Not allowed"}, status=403)

    # total products
    total_products = Product.objects.filter(vendor=request.user).count()

    # total orders (based on vendor products)
    order_items = OrderItem.objects.filter(product__vendor=request.user)

    total_orders = order_items.count()

    # total revenue
    revenue = order_items.aggregate(total=Sum('product__price'))['total'] or 0

    return Response({
        "total_products": total_products,
        "total_orders": total_orders,
        "revenue": revenue
    })
