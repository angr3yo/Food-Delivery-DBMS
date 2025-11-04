from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection, transaction
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
import random
from django.db.models import Max

import decimal
from .models import Orders, PaymentMethods, Restaurants
from django.utils import timezone

from .models import (
    Customers, Profile, Restaurants, MenuItems,
    PaymentMethods, Orders, OrderItems,
    Employees, Vehicles, OrderAssignment
)

from decimal import Decimal


assigned_employee = Employees.objects.filter(role="Driver").order_by("?").first()

# Select a random vehicle (if applicable)
assigned_vehicle = Vehicles.objects.order_by("?").first()



# --- AUTHENTICATION VIEWS ---

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                first_name = request.POST.get('first_name', user.username)
                last_name = request.POST.get('last_name', '')
                phone = request.POST.get('phone', '')

                # Create customer
                customer = Customers.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone
                )

                # Create profile (link auth_user + customer)
                role = 'ADMIN' if user.is_staff else 'CUSTOMER'
                Profile.objects.create(
                    user=user,
                    customer_profile=customer,
                    role=role
                )

                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('home')

            except Exception as e:
                user.delete()  # rollback user creation if failure
                messages.error(request, f'Error creating profile: {e}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# --- CORE APP VIEWS ---

@login_required
def home(request):
    """Home page — shows all restaurants and their menus."""
    restaurants = Restaurants.objects.all().order_by('name')
    menu_items = MenuItems.objects.select_related('restaurant').all()

    restaurant_menus = {}
    for item in menu_items:
        restaurant_menus.setdefault(item.restaurant.restaurant_id, []).append(item)

    return render(request, 'home.html', {
        'restaurants': restaurants,
        'restaurant_menus': restaurant_menus
    })


@login_required
def menu(request, rid):
    """Displays all menu items for a restaurant."""
    try:
        restaurant = Restaurants.objects.get(restaurant_id=rid)
        menu_items = MenuItems.objects.filter(restaurant=restaurant)
        return render(request, 'menu.html', {'restaurant': restaurant, 'menu_items': menu_items})
    except Restaurants.DoesNotExist:
        messages.error(request, 'Restaurant not found.')
        return redirect('home')


# --- CUSTOMER PROFILE & ORDERS ---

@login_required
def customer_profile(request):
    try:
        customer = request.user.profile.customer_profile
        order_count = Orders.objects.filter(customer=customer).count()
        payment_methods = PaymentMethods.objects.filter(customer=customer)
        total_spend = sum(pm.total_spend or 0 for pm in payment_methods)
        return render(request, 'customer_profile.html', {
            'customer': customer,
            'orders': order_count,
            'spend': total_spend
        })
    except Profile.DoesNotExist:
        messages.error(request, "Your profile is incomplete.")
        return redirect('home')


@login_required
def my_orders(request):
    try:
        customer = request.user.profile.customer_profile
        orders = Orders.objects.filter(customer=customer).order_by('-order_id')
        return render(request, 'my_orders.html', {'orders': orders})
    except Exception as e:
        messages.error(request, f"Could not load your orders: {e}")
        return redirect('home')



@login_required
def order_confirmation(request, order_id):
    try:
        # Fetch order with restaurant and payment info
        order = Orders.objects.select_related('restaurant', 'payment').get(order_id=order_id)

        # ✅ Fetch assignment directly from DB (refreshed every time)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    oa.Order_id, 
                    e.Employee_id, 
                    e.Employee_name, 
                    e.Phone, 
                    v.Vehicle_id, 
                    v.Type, 
                    v.Registration_Number
                FROM Order_Assignment oa
                JOIN Employees e ON oa.Employee_id = e.Employee_id
                JOIN Vehicles v ON oa.Vehicle_id = v.Vehicle_id
                WHERE oa.Order_id = %s
                ORDER BY oa.Assignment_Time DESC
                LIMIT 1;
            """, [order_id])
            row = cursor.fetchone()

        assignment = None
        if row:
            assignment = {
                'order_id': row[0],
                'employee': {
                    'id': row[1],
                    'name': row[2],
                    'phone': row[3]
                },
                'vehicle': {
                    'id': row[4],
                    'type': row[5],
                    'registration_number': row[6]
                }
            }

        # ✅ Fetch items correctly
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    oi.Item_id, 
                    m.Item_Name, 
                    m.Price, 
                    oi.Quantity
                FROM Order_Items oi
                JOIN Menu_Items m ON oi.Item_id = m.Item_id
                WHERE oi.Order_id = %s;
            """, [order_id])
            items_rows = cursor.fetchall()

        items = [
            {
                'item_id': r[0],
                'name': r[1],
                'price': r[2],
                'quantity': r[3],
            } for r in items_rows
        ]

        return render(request, 'order_confirmation.html', {
            'order': order,
            'items': items,
            'assignment': assignment,
        })

    except Orders.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('home')
    except Exception as e:
        messages.error(request, f"Error loading order details: {e}")
        return redirect('home')




# --- CART VIEWS ---
def get_cart(request):
    """Retrieve or initialize the cart from session"""
    return request.session.get('cart', {})

def save_cart(request, cart):
    """Save updated cart to session"""
    request.session['cart'] = cart
    request.session.modified = True
    
def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
        request.session.modified = True



@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(MenuItems, pk=item_id)
    restaurant_id = str(item.restaurant.restaurant_id)
    cart = get_cart(request)

    # If cart has items from a different restaurant, clear it
    if cart and list(cart.keys())[0] != restaurant_id:
        messages.info(request, "Cart cleared because you added an item from a different restaurant.")
        cart = {}

    # Add or update the item
    if restaurant_id not in cart:
        cart[restaurant_id] = {}

    item_id_str = str(item_id)
    if item_id_str in cart[restaurant_id]:
        cart[restaurant_id][item_id_str]['quantity'] += 1
    else:
        cart[restaurant_id][item_id_str] = {
            'name': item.item_name,
            'price': float(item.price),
            'quantity': 1,
            'image_url': '/static/images/default_food.jpg'  # default fallback
        }

    save_cart(request, cart)
    return redirect('view_cart')



@login_required
def remove_from_cart(request, item_id):
    """Removes an item from the cart."""
    cart = request.session.get('cart', {})
    cart_items = cart.get('items', {})
    item_key = str(item_id)

    if item_key in cart_items:
        del cart_items[item_key]
        messages.info(request, "Item removed from cart.")

    if not cart_items:
        cart = {}
    else:
        cart['items'] = cart_items

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('view_cart')


@login_required
def view_cart(request):
    cart = get_cart(request)
    total = 0
    cart_items = []
    restaurant = None  # Default

    if cart:
        # Safely get restaurant_id (first key in cart)
        restaurant_id = list(cart.keys())[0]

        # ✅ Ensure restaurant_id is numeric before querying
        if str(restaurant_id).isdigit():
            try:
                restaurant = Restaurants.objects.get(pk=int(restaurant_id))
            except Restaurants.DoesNotExist:
                restaurant = None
        else:
            restaurant = None  # Prevent ValueError if key is invalid

        # ✅ Process cart items only if restaurant_id is valid
        if restaurant:
            for item_id, data in cart[str(restaurant_id)].items():
                item_total = data['price'] * data['quantity']
                total += item_total
                cart_items.append({
                    'id': item_id,
                    'name': data['name'],
                    'price': data['price'],
                    'quantity': data['quantity'],
                    'total': item_total,
                    'image_url': data['image_url']
                })

    # ✅ Handle user payment methods
    from .models import PaymentMethods, Customers
    # ✅ Handle user payment methods
    user_customer = request.user.profile.customer_profile
    existing_methods = PaymentMethods.objects.filter(customer=user_customer)

    # If no payment methods exist, still offer UPI/Cash/Card options
    available_methods = [pm.payment_type for pm in existing_methods] if existing_methods else []
    default_methods = ["UPI", "Cash", "Card"]

    # Merge both and remove duplicates (in case user already has one)
    payment_methods = sorted(set(available_methods + default_methods))

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': round(total, 2),
        'payment_methods': payment_methods,
        'restaurant': restaurant,
    })





@login_required
@transaction.atomic
@transaction.atomic
def place_order(request):
    cart = get_cart(request)
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')

    restaurant_id = list(cart.keys())[0]
    restaurant = Restaurants.objects.get(pk=int(restaurant_id))
    payment_type = request.POST.get('payment_type')

    if not payment_type:
        messages.error(request, "Please select a payment method.")
        return redirect('view_cart')

    user_customer = request.user.profile.customer_profile

    # ✅ Explicitly create or get payment method with valid primary key
    payment_method, created = PaymentMethods.objects.get_or_create(
        customer=user_customer,
        payment_type=payment_type,
        defaults={'total_spend': Decimal('0.00')}
    )

    # ✅ Ensure payment_id exists
    if not payment_method.payment_id:
        payment_method.save()

    # Calculate total
    total = sum(
        Decimal(item['price']) * item['quantity']
        for item in cart[str(restaurant_id)].values()
    )

    # Update spend
    payment_method.total_spend += total
    payment_method.save()

    # Create order with valid payment reference
    order = Orders.objects.create(
        customer=user_customer,
        restaurant=restaurant,
        payment=payment_method,
        total_price=total,
        delivery_status="Pending"
    )

    # Add items
    for item_id, data in cart[str(restaurant_id)].items():
        OrderItems.objects.create(
            order=order,
            item_id=item_id,
            quantity=data['quantity']
        )

    # Assign driver
    try:
        assigned_employee = Employees.objects.filter(role="Driver").order_by("?").first()
        if not assigned_employee:
            raise Exception("No available driver found.")

        with connection.cursor() as cursor:
            cursor.callproc('AssignOrderDriver', [order.order_id, assigned_employee.employee_id])

    except Exception as e:
        messages.error(request, f"Error assigning driver: {e}")
        clear_cart(request)
        return redirect('view_cart')

    clear_cart(request)
    messages.success(
        request,
        f"Order #{order.order_id} placed successfully using {payment_method.payment_type}!"
    )
    return redirect('order_confirmation', order_id=order.order_id)
@login_required
def update_quantity(request, item_id, action):
    cart = get_cart(request)
    if not cart:
        return redirect('view_cart')

    restaurant_id = list(cart.keys())[0]
    item_id_str = str(item_id)

    if item_id_str in cart[restaurant_id]:
        if action == 'increase':
            cart[restaurant_id][item_id_str]['quantity'] += 1
        elif action == 'decrease':
            if cart[restaurant_id][item_id_str]['quantity'] > 1:
                cart[restaurant_id][item_id_str]['quantity'] -= 1
            else:
                del cart[restaurant_id][item_id_str]
                # Delete restaurant if no items left
                if not cart[restaurant_id]:
                    del cart[restaurant_id]

    save_cart(request, cart)
    return redirect('view_cart')