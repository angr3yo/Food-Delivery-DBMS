from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection, transaction
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Customers, Profile, Restaurants, MenuItems, PaymentMethods, Orders, OrderItems, Employees, Vehicles, OrderAssignment
import random

# --- AUTHENTICATION VIEWS ---


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # CRITICAL FIX: Create Customer and Profile for the new user
            try:
                # Use form data to create a Customer
                # NOTE: This assumes your signup form will be expanded to include these fields.
                # For now, we use placeholders.
                customer = Customers.objects.create(
                    customer_id=random.randint(
                        200000, 999999),  # Generate random ID
                    first_name=request.POST.get('first_name', user.username),
                    last_name=request.POST.get('last_name', 'User'),
                    phone=request.POST.get(
                        'phone', '0000000000')  # Placeholder phone
                )

                # Create the Profile to link User and Customer
                Profile.objects.create(
                    user=user, customer_profile=customer, role='CUSTOMER')

                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('home')
            except Exception as e:
                # If Customer/Profile creation fails, delete the user to avoid orphans
                user.delete()
                messages.error(
                    request, f'Error creating profile: {e}. Please try again.')

    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')  # Redirect to login page as requested


# --- CORE APP VIEWS ---

@login_required
def home(request):
    """
    Home page view – displays all restaurants.
    Uses the Django ORM.
    """
    restaurants = Restaurants.objects.all().order_by('name')
    return render(request, 'home.html', {'restaurants': restaurants})


@login_required
def menu(request, rid):
    """
    Menu page view — displays all menu items for the selected restaurant.
    Uses the Django ORM.
    """
    try:
        restaurant = Restaurants.objects.get(restaurant_id=rid)
        # Use the ORM to fetch items, using the 'restaurant' foreign key
        menu_items = MenuItems.objects.filter(restaurant=restaurant)

        context = {
            'restaurant': restaurant,
            'menu_items': menu_items,
        }
        return render(request, 'menu.html', context)
    except Restaurants.DoesNotExist:
        messages.error(request, 'Restaurant not found.')
        return redirect('home')


@login_required
def customer_profile(request):
    """
    Displays the logged-in customer's profile.
    """
    try:
        # Get customer from the logged-in user's profile
        customer = request.user.profile.customer_profile

        # Use the ORM to get stats
        order_count = Orders.objects.filter(customer=customer).count()

        # Get total spend from the PaymentMethods table
        payment_methods = PaymentMethods.objects.filter(customer=customer)
        total_spend = sum(
            pm.total_spend for pm in payment_methods if pm.total_spend)

        context = {
            'customer': customer,
            'orders': order_count,
            'spend': total_spend,
        }
        return render(request, 'customer_profile.html', context)
    except Profile.DoesNotExist:
        messages.error(
            request, "Your customer profile is not set up correctly.")
        return redirect('home')
    except Exception as e:
        messages.error(request, f"Could not load your profile. {e}")
        return redirect('home')


@login_required
def my_orders(request):
    """
    Displays the logged-in customer's order history.
    """
    try:
        customer = request.user.profile.customer_profile
        # FIX IS HERE: Changed 'order_date' to 'order_id' to prevent the crash
        orders = Orders.objects.filter(customer=customer).order_by('-order_id')

        context = {
            'orders': orders,
        }
        return render(request, 'my_orders.html', context)
    except Profile.DoesNotExist:
        messages.error(
            request, "Your customer profile is not set up correctly.")
        return redirect('home')
    except Exception as e:
        messages.error(request, f"Could not load your orders. {e}")
        return redirect('home')


@login_required
def order_confirmation(request, order_id):
    """
    Shows the full details of a just-placed order, including driver assignment.
    """
    try:
        customer = request.user.profile.customer_profile
        order = Orders.objects.get(order_id=order_id, customer=customer)
        # Fetch related items using the ORM relationship defined in models
        # Assumes OrderItems.order links correctly
        items = OrderItems.objects.filter(order=order)

        # Use select_related for efficiency
        assignment = OrderAssignment.objects.select_related(
            'employee', 'vehicle').get(order=order)

        context = {
            'order': order,
            'items': items,
            'assignment': assignment,
        }
        return render(request, 'order_confirmation.html', context)
    except Orders.DoesNotExist:
        messages.error(request, "Order not found.")
        # Redirect to order list if specific order not found
        return redirect('my_orders')
    # Be specific about the assignment error
    except OrderAssignment.DoesNotExist:
        messages.warning(
            request, "Order placed, but assignment is still pending.")
        # Allow viewing the order even if assignment failed for some reason
        order = Orders.objects.get(order_id=order_id, customer=customer)
        items = OrderItems.objects.filter(order=order)
        context = {
            'order': order,
            'items': items,
            'assignment': None,  # Indicate no assignment found
        }
        return render(request, 'order_confirmation.html', context)
    except Profile.DoesNotExist:
        messages.error(request, "Your customer profile is missing.")
        return redirect('home')
    except Exception as e:
        messages.error(
            request, f"An error occurred loading order details: {e}")
        return redirect('my_orders')

# --- CART VIEWS ---


@login_required
def add_to_cart(request, item_id):
    if request.method == 'POST':
        item = None  # Define item here to ensure it's available for the final redirect
        try:
            item = MenuItems.objects.get(item_id=item_id)
            cart = request.session.get('cart', {})

            # Check if cart is empty or if item is from the same restaurant
            cart_restaurant_id = cart.get('restaurant_id')
            if not cart_restaurant_id:
                # Cart is empty, set the restaurant
                cart['restaurant_id'] = item.restaurant.restaurant_id
                cart['restaurant_name'] = item.restaurant.name
            # FIX: Changed 'restaurant_fsid' to 'restaurant_id'
            elif cart_restaurant_id != item.restaurant.restaurant_id:
                # Item is from a different restaurant
                messages.warning(
                    request, f"You can only order from one restaurant at a time. Your cart from {cart.get('restaurant_name')} has been cleared.")
                cart = {
                    'restaurant_id': item.restaurant.restaurant_id,
                    'restaurant_name': item.restaurant.name
                }

            # Add/update item in cart
            item_key = str(item_id)
            if item_key in cart:
                # Ensure quantity exists and is an int
                if isinstance(cart[item_key], dict) and isinstance(cart[item_key].get('quantity'), int):
                    cart[item_key]['quantity'] += 1
                else:  # If structure is wrong, reset it
                    cart[item_key] = {
                        'id': item.item_id,
                        'name': item.item_name,
                        'price': float(item.price),
                        'quantity': 1,
                    }
            else:
                cart[item_key] = {
                    'id': item.item_id,
                    'name': item.item_name,
                    'price': float(item.price),
                    'quantity': 1,
                }

            request.session['cart'] = cart
            messages.success(request, f"Added {item.item_name} to cart.")

        except MenuItems.DoesNotExist:
            messages.error(request, "Item not found.")
            # If item doesn't exist, we can't redirect based on it
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Error adding item to cart: {e}")
            # Decide on a safe redirect if item might be None
            return redirect('home')

        # Redirect safely, ensuring item exists
        if item:
            return redirect('menu', rid=item.restaurant.restaurant_id)
        else:
            # Fallback if item somehow became None after initial fetch but before redirect
            return redirect('home')

    # If not POST, redirect home or to previous page if available
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    item_key = str(item_id)

    if item_key in cart:
        del cart[item_key]
        messages.info(request, "Item removed from cart.")

    # Check if cart is now empty (only has restaurant info left)
    # Use <= 2 to account for potential structure variations if needed, safer than ==
    if len(cart.keys() - {'restaurant_id', 'restaurant_name'}) == 0:
        request.session['cart'] = {}  # Clear cart completely
    else:
        request.session['cart'] = cart

    return redirect('view_cart')


@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    # Ensure items are dictionaries before processing
    for key, value in cart.items():
        # Explicitly check the type and that it's an item entry
        if isinstance(value, dict) and 'id' in value and 'quantity' in value and 'price' in value:
            item_price = float(value.get('price', 0))  # Ensure price is float
            # Ensure quantity is int
            item_quantity = int(value.get('quantity', 0))

            value['total'] = item_price * item_quantity
            total_price += value['total']
            cart_items.append(value)
        elif key not in ['restaurant_id', 'restaurant_name']:
            # Log or handle unexpected cart item structure if necessary
            print(
                f"Warning: Unexpected item structure in cart for key {key}: {value}")

    # Get payment methods for the user
    payment_methods = []  # Default to empty list
    try:
        customer = request.user.profile.customer_profile
        payment_methods = PaymentMethods.objects.filter(customer=customer)

        # If user has no payment methods, create a default "Cash" one for them
        if not payment_methods.exists():
            # Ensure a payment ID is generated correctly and doesn't conflict
            max_id = PaymentMethods.objects.order_by('-payment_id').first()
            new_payment_id = (max_id.payment_id + 1) if max_id else 700

            default_payment = PaymentMethods.objects.create(
                payment_id=new_payment_id,
                customer=customer,
                payment_type='Cash',
                total_spend=0.00  # Initialize total_spend
            )
            payment_methods = [default_payment]

    except Profile.DoesNotExist:
        messages.error(
            request, "Your customer profile is not set up correctly.")
        # Handle case where profile might not exist yet
    except Exception as e:
        messages.error(request, f"Could not load payment methods: {e}")
        # payment_methods remains an empty list

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'restaurant_id': cart.get('restaurant_id'),
        'restaurant_name': cart.get('restaurant_name'),
        'payment_methods': payment_methods,
    }
    return render(request, 'cart.html', context)


@login_required
@transaction.atomic  # Ensures all database operations succeed or fail together
def place_order(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        payment_id = request.POST.get('payment_id')

        try:
            customer = request.user.profile.customer_profile
            restaurant_id = cart.get('restaurant_id')

            if not restaurant_id or not payment_id:
                messages.error(
                    request, "Cart is empty or no payment method selected.")
                return redirect('view_cart')

            # 1. Get a valid payment method
            payment_method = PaymentMethods.objects.get(
                payment_id=payment_id, customer=customer)

            # --- Call Stored Procedure to create the Order ---
            new_order_id = None  # Initialize to None
            with connection.cursor() as cursor:
                cursor.callproc('sp_CreatePendingOrder', [
                                customer.customer_id, restaurant_id, payment_method.payment_id])
                result = cursor.fetchone()
                if result is None:
                    raise Exception(
                        "Stored procedure sp_CreatePendingOrder did not return an order ID.")
                new_order_id = result[0]

                # 2. Add items to the order using the second stored procedure
                item_added = False  # Flag to check if at least one item was processed
                for key, value in cart.items():
                    # Check if it's a valid item dictionary
                    if isinstance(value, dict) and 'id' in value and 'quantity' in value:
                        item_id = value.get('id')
                        quantity = value.get('quantity')
                        # Ensure values are not None before calling SP
                        if item_id is not None and quantity is not None:
                            cursor.callproc('sp_AddItemToOrder', [
                                            new_order_id, item_id, quantity])
                            item_added = True

                if not item_added:
                    # If the loop finished but no items were added (e.g., cart only had restaurant info)
                    raise Exception(
                        "No valid items found in the cart to add to the order.")

            # Ensure new_order_id was set before proceeding
            if new_order_id is None:
                raise Exception(
                    "Failed to retrieve new order ID after calling stored procedure.")

            # 3. Assign a random driver and vehicle (using ORM)
            # Fetch the order instance using the ID from the stored procedure
            # NOTE: We fetch it *after* items are added and price is potentially updated by triggers
            try:
                # It's possible the instance isn't immediately visible if transaction isolation levels are high,
                # but typically Django's transaction management handles this.
                order_instance = Orders.objects.get(order_id=new_order_id)
            except Orders.DoesNotExist:
                # This would be unusual if the SP succeeded, but handle it.
                raise Exception(
                    f"Order with ID {new_order_id} not found after creation.")

            available_employees = Employees.objects.filter(
                supervises_employee__isnull=False).order_by('?')
            available_vehicles = Vehicles.objects.order_by('?')

            if available_employees.exists() and available_vehicles.exists():
                random_driver = available_employees.first()
                random_vehicle = available_vehicles.first()

                # FIX: Explicitly use order_id for the assignment's primary key
                OrderAssignment.objects.create(
                    order_id=new_order_id,  # Use the ID directly as the PK
                    employee=random_driver,
                    vehicle=random_vehicle
                )

            else:
                messages.warning(
                    request, "Order placed, but no drivers or vehicles were available for immediate assignment.")

            # 4. Clear the cart from the session
            request.session['cart'] = {}

            messages.success(request, "Order placed successfully!")
            return redirect('order_confirmation', order_id=new_order_id)

        except Profile.DoesNotExist:
            messages.error(request, "Your customer profile is missing.")
            return redirect('home')  # Or perhaps a profile setup page
        except PaymentMethods.DoesNotExist:
            messages.error(request, "Invalid payment method selected.")
            return redirect('view_cart')
        # Catch potential issue during OrderAssignment creation more specifically if needed
        # except IntegrityError as ie: ...
        except Exception as e:
            messages.error(
                request, f"An error occurred while placing your order: {e}")
            # Rollback happens automatically with @transaction.atomic
            return redirect('view_cart')

    # If not POST, redirect to cart view
    return redirect('view_cart')
