from django.contrib import admin
from .models import (
    Profile, Address, CustomerAddresses, Customers, Employees,
    MenuItems, OrderAssignment, OrderItems, Orders,
    PaymentMethods, Restaurants, Vehicles
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# --- Inlines ---


class ProfileInline(admin.StackedInline):
    """Shows the Profile model inside the User admin page."""
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomerAddressInline(admin.TabularInline):
    """Shows the CustomerAddress link inside the Customer admin page."""
    model = CustomerAddresses
    extra = 0  # Don't show extra blank forms
    verbose_name = "Customer Address Link"
    verbose_name_plural = "Customer Address Links"
    readonly_fields = ('customer', 'address')  # Make inline read-only

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# --- Custom Admin Models ---


class CustomUserAdmin(BaseUserAdmin):
    """Adds the Profile inline to the default User admin."""
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


class ReadOnlyAdmin(admin.ModelAdmin):
    """
    A base class that makes a model read-only in the admin.
    It also prevents adding or deleting objects.
    """

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        # Allow viewing but not changing
        if request.method == 'POST':
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        # Make all fields read-only
        if self.model:
            # Ensure all fields from the model are included, handling potential missing fields
            readonly_fields_list = []
            for f in self.model._meta.get_fields():
                # Include only concrete fields and foreign keys usable in admin
                if hasattr(f, 'column') and f.concrete:
                    readonly_fields_list.append(f.name)
                elif f.is_relation and (f.one_to_one or (f.many_to_one and f.related_model)):
                    readonly_fields_list.append(f.name)
            return readonly_fields_list
        return []


class CustomerAdmin(ReadOnlyAdmin):
    """Read-only admin for Customers, with addresses shown inline."""
    inlines = (CustomerAddressInline,)
    list_display = ('customer_id', 'first_name', 'last_name', 'phone')
    search_fields = ('first_name', 'last_name', 'phone')

# --- REVISED FIX for OrderAdmin ---


class OrderAdmin(ReadOnlyAdmin):
    """Read-only admin for Orders."""
    # Define display and filter fields based on model introspection
    _list_display = ['order_id', 'customer',
                     'restaurant', 'payment', 'total_price']
    _list_filter = ['restaurant']
    _search_fields = ['order_id',
                      'customer__first_name', 'customer__last_name']

    # Dynamically add order_date and status if they exist on the model
    if hasattr(Orders, 'order_date'):
        _list_display.append('order_date')
        _list_filter.append('order_date')
    if hasattr(Orders, 'status'):
        _list_display.append('status')
        _list_filter.append('status')

    list_display = tuple(_list_display)
    list_filter = tuple(_list_filter)
    search_fields = tuple(_search_fields)

    # get_readonly_fields is inherited from ReadOnlyAdmin


class OrderItemAdmin(ReadOnlyAdmin):
    """Read-only admin for OrderItems."""
    list_display = ('order', 'item', 'quantity')
    search_fields = ('order__order_id', 'item__item_name')


class RestaurantAdmin(ReadOnlyAdmin):
    """Read-only admin for Restaurants."""
    list_display = ('restaurant_id', 'name', 'cuisine', 'address')
    list_filter = ('cuisine',)
    search_fields = ('name', 'cuisine')


class MenuItemAdmin(ReadOnlyAdmin):
    """Read-only admin for MenuItems."""
    list_display = ('item_id', 'item_name', 'restaurant', 'price')
    list_filter = ('restaurant',)
    search_fields = ('item_name', 'restaurant__name')


class EmployeeAdmin(ReadOnlyAdmin):
    """Read-only admin for Employees."""
    list_display = ('employee_id', 'employee_name',
                    'phone', 'supervises_employee','role')
    search_fields = ('employee_name', 'phone')


class VehicleAdmin(ReadOnlyAdmin):
    """Read-only admin for Vehicles."""
    list_display = ('vehicle_id', 'registration_number', 'type')
    list_filter = ('type',)
    search_fields = ('registration_number',)


class PaymentMethodAdmin(ReadOnlyAdmin):
    """Read-only admin for PaymentMethods."""
    list_display = ('payment_id', 'customer', 'payment_type', 'total_spend')
    search_fields = ('customer__first_name', 'payment_type')


class AddressAdmin(ReadOnlyAdmin):
    """Read-only admin for Addresses."""
    list_display = ('address_id', 'address_line_1', 'state', 'zipcode')
    search_fields = ('address_line_1', 'zipcode')


class OrderAssignmentAdmin(ReadOnlyAdmin):
    """Read-only admin for OrderAssignments."""
    list_display = ('order', 'employee', 'vehicle', 'assignment_time')
    search_fields = ('order__order_id', 'employee__employee_name')


# --- Registration ---

# Unregister the default User admin
admin.site.unregister(User)
# Register the new User admin with the Profile inline
admin.site.register(User, CustomUserAdmin)

# Register all the "managed=False" models as read-only
admin.site.register(Customers, CustomerAdmin)
admin.site.register(Orders, OrderAdmin)  # Using the updated OrderAdmin
admin.site.register(OrderItems, OrderItemAdmin)
admin.site.register(Restaurants, RestaurantAdmin)
admin.site.register(MenuItems, MenuItemAdmin)
admin.site.register(Employees, EmployeeAdmin)
admin.site.register(Vehicles, VehicleAdmin)
admin.site.register(PaymentMethods, PaymentMethodAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(OrderAssignment, OrderAssignmentAdmin)

# We don't need to register CustomerAddresses, it's an inline
# admin.site.register(CustomerAddresses)
