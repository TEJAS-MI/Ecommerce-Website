from django.shortcuts import render
from .models import Product, Order, Customer, OrderItem
from django.http import JsonResponse
import json

# ====================================================================
# NEW UTILITY FUNCTION: Read Guest Cart Data from Browser Cookie
# ====================================================================

def cookieCart(request):
    """
    Retrieves the cart data for an anonymous user from the browser cookie.
    Formats the data structure to match the authenticated user's Order data.
    """
    try:
        # 1. Get the cart data string from the browser's cookie (sent from JS)
        cart = json.loads(request.COOKIES.get('cart', '{}'))
    except:
        # If cookie is corrupt or not set, default to an empty cart
        cart = {}
        
    print('Cookie Cart:', cart) # Debugging log for server

    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']

    # 2. Loop through the cookie data to build the necessary context variables
    for p_id in cart:
        try:
            # Ensure the product ID is valid before using it
            product_id = int(p_id)
            quantity = cart[p_id]['quantity']
            
            # Skip items with no quantity
            if quantity <= 0:
                continue

            cartItems += quantity
            
            product = Product.objects.get(id=product_id)
            total = (product.price * quantity)

            order['get_cart_total'] += total
            order['get_cart_items'] += quantity

            # Build the item structure (to match how authenticated items are passed)
            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    # NOTE: Ensure your Product model has an imageURL property
                    'imageURL': product.imageURL 
                },
                'quantity': quantity,
                'get_total': total,
            }
            items.append(item)
        except Exception as e:
            # Catch exceptions for corrupt data or non-existent product IDs
            print(f"Error processing item {p_id} in cookie: {e}")
            pass
            
    return {'cartItems': cartItems, 'order': order, 'items': items}


# ====================================================================
# CORE VIEWS (UPDATED to handle both authenticated and guest users)
# ====================================================================

def store(request):
    # Determine which cart data structure to use
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        # items = order.orderitem_set.all() # Not strictly needed for store view
        cartItems = order.get_cart_items
        
    else:
        # Use the utility function for anonymous users
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


# ====================================================================
# ⭐ NEW VIEW FUNCTION FOR PRODUCT DETAILS (The solution you requested)
# ====================================================================

def productDetail(request, pk):
    """ 
    Renders the details page for a single product based on its primary key (pk).
    Also passes cart item count for the header/navbar.
    """
    
    # Determine which cart data structure to use for the navbar/header
    if request.user.is_authenticated:
        customer = request.user.customer
        # Use .first() to prevent GetQueryset errors if a user logs in mid-checkout
        order = Order.objects.filter(customer=customer, complete=False).first()
        cartItems = order.get_cart_items if order else 0
        
    else:
        # Use the utility function for anonymous users
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        
    try:
        # Fetch the specific product using the primary key (pk) passed in the URL
        product = Product.objects.get(id=pk)
    except Product.DoesNotExist:
        # Handle case where the product ID is invalid (optional)
        product = None 
    
    context = {'product': product, 'cartItems': cartItems}
    # NOTE: You must create 'store/product_detail.html' template
    return render(request, 'store/product_detail.html', context)

# ====================================================================
# REST OF YOUR EXISTING VIEWS
# ====================================================================

def cart(request):
    """ Render the cart page with current order items. """
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        
    else:
        # Use the utility function for anonymous users
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    # NOTE: You must now update your cart.html to handle the structure of 'items' 
    # for guest users (which is a list of dictionaries, not queryset objects)
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    """ Render the checkout page with current order items. """
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    else:
        # Use the utility function for anonymous users
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


# --- AJAX View for Cart Updates (This part remains for logged-in users) ---

def updateItem(request):
    """
    Update quantity of a product in the cart via AJAX.
    NOTE: This is currently only used for authenticated users.
    """
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('Product ID:', productId)

    # Security check: Ensure user is authenticated before proceeding with DB update
    if not request.user.is_authenticated:
        return JsonResponse("User not logged in. Cannot update database.", safe=False, status=403)

    # 1. Get Customer and Product instances
    customer = request.user.customer
    product = Product.objects.get(id=productId)

    # 2. Get or create the active order
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    # 3. Get or create the OrderItem for this product
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    # 4. Update quantity based on action
    if action == 'add':
        orderItem.quantity = (orderItem.quantity or 0) + 1
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity or 0) - 1

    # 5. Save OrderItem and delete if quantity <= 0
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()

    # 6. Return JSON response
    return JsonResponse("Item was successfully updated", safe=False)

def processOrder(request):
    # NOTE: This function would also need to be updated to handle guest checkouts!
    return JsonResponse('payment submitted',safe=False)