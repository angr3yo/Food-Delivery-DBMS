from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

# ----------------------------
# User Profile (same as before)
# ----------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_profile = models.OneToOneField(
        'Customers', on_delete=models.CASCADE, null=True, blank=True)
    employee_profile = models.OneToOneField(
        'Employees', on_delete=models.CASCADE, null=True, blank=True)

    ROLE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('ADMIN', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CUSTOMER')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    @property
    def is_admin(self):
        return self.role == 'ADMIN'


# ----------------------------
# Address
# ----------------------------
class Address(models.Model):
    address_id = models.AutoField(db_column='Address_id', primary_key=True)
    address_line_1 = models.CharField(db_column='Address_line_1', max_length=100)
    state = models.CharField(db_column='State', max_length=50)
    country = models.CharField(db_column='Country', max_length=50)
    zipcode = models.CharField(db_column='Zipcode', max_length=10)

    class Meta:
        managed = False
        db_table = 'Address'
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.address_line_1} ({self.zipcode})"


# ----------------------------
# Customers
# ----------------------------
class Customers(models.Model):
    customer_id = models.AutoField(db_column='Customer_id', primary_key=True)
    first_name = models.CharField(db_column='First_name', max_length=50)
    middle_name = models.CharField(db_column='Middle_name', max_length=50, blank=True, null=True)
    last_name = models.CharField(db_column='Last_name', max_length=50)
    phone = models.CharField(db_column='Phone', unique=True, max_length=15)

    class Meta:
        managed = False  # ✅ allow Django to manage model (creates proper AutoField)
        db_table = 'Customers'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ----------------------------
# Employees
# ----------------------------
class Employees(models.Model):
    employee_id = models.IntegerField(primary_key=True, db_column='Employee_id')
    employee_name = models.CharField(max_length=100, db_column='Employee_name')
    phone = models.CharField(max_length=15, unique=True, db_column='Phone')
    supervises_employee = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='Supervises_Employee_id'
    )
    role = models.CharField(max_length=50, db_column='Role', default='Driver')

    class Meta:
        managed = False
        db_table = 'Employees'

    def __str__(self):
        return f"{self.employee_name} ({self.role})"



# ----------------------------
# Vehicles
# ----------------------------
class Vehicles(models.Model):
    vehicle_id = models.AutoField(db_column='Vehicle_id', primary_key=True)
    registration_number = models.CharField(db_column='Registration_number', unique=True, max_length=20)
    type = models.CharField(db_column='Type', max_length=10)

    class Meta:
        managed = False
        db_table = 'Vehicles'

    def __str__(self):
        return f"{self.registration_number} ({self.type})"


# ----------------------------
# Restaurants
# ----------------------------
class Restaurants(models.Model):
    restaurant_id = models.AutoField(db_column='Restaurant_id', primary_key=True)
    name = models.CharField(db_column='Name', max_length=100)
    address = models.ForeignKey(Address, models.DO_NOTHING, db_column='Address_id')
    cuisine = models.CharField(db_column='Cuisine', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Restaurants'

    def __str__(self):
        return self.name


# ----------------------------
# Menu Items
# ----------------------------
class MenuItems(models.Model):
    item_id = models.AutoField(db_column='Item_id', primary_key=True)
    restaurant = models.ForeignKey(Restaurants, models.DO_NOTHING, db_column='Restaurant_id')
    item_name = models.CharField(db_column='Item_Name', max_length=100)
    description = models.CharField(db_column='Description', max_length=255, blank=True, null=True)
    price = models.DecimalField(db_column='Price', max_digits=6, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'Menu_Items'

    def __str__(self):
        return self.item_name



# ----------------------------
# Payment Methods
# ----------------------------
class PaymentMethods(models.Model):
    payment_id = models.AutoField(
        db_column='Payment_id',
        primary_key=True
    )
    customer = models.ForeignKey(
        'Customers',
        on_delete=models.CASCADE,
        db_column='Customer_id'
    )
    total_spend = models.DecimalField(
        db_column='Total_Spend',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')  # ✅ ensures non-null total
    )
    payment_type = models.CharField(
        db_column='Payment_type',
        max_length=20
    )

    class Meta:
        managed = False  # ✅ keeps Django from trying to create this table again
        db_table = 'Payment_Methods'
        unique_together = (('customer', 'payment_type'),)  # ✅ ensures one per type per customer

    def __str__(self):
        return f"{self.payment_type} - {self.customer.first_name} (ID: {self.payment_id})"




# ----------------------------
# Orders
# ----------------------------
class Orders(models.Model):
    order_id = models.AutoField(primary_key=True, db_column='Order_id')
    customer = models.ForeignKey('Customers', on_delete=models.CASCADE, db_column='Customer_id')
    restaurant = models.ForeignKey('Restaurants', on_delete=models.CASCADE, db_column='Restaurant_id')
    payment = models.ForeignKey('PaymentMethods', on_delete=models.CASCADE, db_column='Payment_id')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, db_column='Total_Price')
    order_date = models.DateTimeField(auto_now_add=True, db_column='Order_Date')
    delivery_status = models.CharField(max_length=20, default='Pending', db_column='Delivery_Status')

    class Meta:
        managed = False
        db_table = 'Orders'

    def __str__(self):
        return f"Order #{self.order_id} - {self.delivery_status}"



# ----------------------------
# Order Items (FIXED - one order → many items)
# ----------------------------
class OrderItems(models.Model):
    order = models.ForeignKey('Orders', on_delete=models.CASCADE, db_column='Order_id')
    item = models.ForeignKey('MenuItems', on_delete=models.CASCADE, db_column='Item_id')
    quantity = models.IntegerField(db_column='Quantity', default=1)

    class Meta:
        db_table = 'Order_Items'
        managed = False  # since it's created directly in MySQL
        unique_together = (('order', 'item'),)




# ----------------------------
# Order Assignment (driver + vehicle)
# ----------------------------
class OrderAssignment(models.Model):
    order = models.OneToOneField(Orders, models.DO_NOTHING, db_column='Order_id', primary_key=True)
    employee = models.ForeignKey(Employees, models.DO_NOTHING, db_column='Employee_id')
    vehicle = models.ForeignKey(Vehicles, models.DO_NOTHING, db_column='Vehicle_id')
    assignment_time = models.DateTimeField(db_column='Assignment_Time', auto_now_add=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Order_Assignment'

    def __str__(self):
        return f"Order {self.order.order_id} → {self.employee.name} ({self.vehicle.registration_number})"




class CustomerAddresses(models.Model):
    # This table has a composite primary key in SQL,
    # but Django ORM needs one field to be a primary key.
    # We'll tell Django that 'customer' is the key for ORM purposes.
    # Field name made lowercase.
    customer = models.OneToOneField(
        'Customers', models.DO_NOTHING, db_column='Customer_id', primary_key=True)
    # Field name made lowercase.
    address = models.ForeignKey(
        Address, models.DO_NOTHING, db_column='Address_id')

    class Meta:
        managed = False
        db_table = 'Customer_Addresses'
        # Represents the composite key
        unique_together = (('customer', 'address'),)
        verbose_name_plural = "Customer Addresses"



