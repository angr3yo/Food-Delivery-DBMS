from django.urls import path
from . import views

urlpatterns = [
    # --- AUTH ---
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # --- CORE ---
    path('', views.home, name='home'),
    path('menu/<int:rid>/', views.menu, name='menu'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<int:order_id>/', views.order_confirmation,
         name='order_confirmation'),

    # --- CART ---
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/',
         views.remove_from_cart, name='remove_from_cart'),
    path('cart/place-order/', views.place_order, name='place_order'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/<str:action>/', views.update_quantity, name='update_quantity'),
]

    # The 'switch_mode' path that caused the error has been removed.

