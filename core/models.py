# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User


# This new Profile model links Django's User to your Customer/Employee tables
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Link to your existing Customer/Employee tables
    # These are nullable because a user is EITHER a customer OR an employee
    customer_profile = models.OneToOneField(
        'Customers', on_delete=models.CASCADE, null=True, blank=True)
    employee_profile = models.OneToOneField(
        'Employees', on_delete=models.CASCADE, null=True, blank=True)

    ROLE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('ADMIN', 'Admin'),
    )
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='CUSTOMER')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    @property
    def is_admin(self):
        return self.role == 'ADMIN'


class Address(models.Model):
    # Field name made lowercase.
    address_id = models.IntegerField(db_column='Address_id', primary_key=True)
    # Field name made lowercase.
    address_line_1 = models.CharField(
        db_column='Address_line_1', max_length=100)
    # Field name made lowercase.
    state = models.CharField(db_column='State', max_length=50)
    # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=50)
    # Field name made lowercase.
    zipcode = models.CharField(db_column='Zipcode', max_length=10)

    class Meta:
        managed = False
        db_table = 'Address'
        verbose_name_plural = "Addresses"  # Fix admin pluralization

    def __str__(self):
        return f"{self.address_line_1} ({self.zipcode})"


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


class Customers(models.Model):
    # Field name made lowercase.
    customer_id = models.IntegerField(
        db_column='Customer_id', primary_key=True)
    # Field name made lowercase.
    first_name = models.CharField(db_column='First_name', max_length=50)
    # Field name made lowercase.
    middle_name = models.CharField(
        db_column='Middle_name', max_length=50, blank=True, null=True)
    # Field name made lowercase.
    last_name = models.CharField(db_column='Last_name', max_length=50)
    # Field name made lowercase.
    phone = models.CharField(db_column='Phone', unique=True, max_length=15)

    class Meta:
        managed = False
        db_table = 'Customers'
        verbose_name_plural = "Customers"

    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.customer_id})"


class Employees(models.Model):
    # Field name made lowercase.
    employee_id = models.IntegerField(
        db_column='Employee_id', primary_key=True)
    # Field name made lowercase.
    employee_name = models.CharField(db_column='Employee_name', max_length=100)
    # Field name made lowercase.
    phone = models.CharField(db_column='Phone', unique=True, max_length=15)
    # Field name made lowercase.
    supervises_employee = models.ForeignKey(
        'self', models.DO_NOTHING, db_column='Supervises_Employee_id', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Employees'
        verbose_name_plural = "Employees"

    def __str__(self):
        return f"{self.employee_name} (ID: {self.employee_id})"


class MenuItems(models.Model):
    # Field name made lowercase.
    item_id = models.IntegerField(db_column='Item_id', primary_key=True)
    # Field name made lowercase.
    restaurant = models.ForeignKey(
        'Restaurants', models.DO_NOTHING, db_column='Restaurant_id')
    # Field name made lowercase.
    item_name = models.CharField(db_column='Item_Name', max_length=100)
    # Field name made lowercase.
    description = models.CharField(
        db_column='Description', max_length=255, blank=True, null=True)
    # Field name made lowercase.
    price = models.DecimalField(
        db_column='Price', max_digits=6, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'Menu_Items'

    def __str__(self):
        return self.item_name


class OrderAssignment(models.Model):
    # Field name made lowercase.
    order = models.OneToOneField(
        'Orders', models.DO_NOTHING, db_column='Order_id', primary_key=True)
    # Field name made lowercase.
    employee = models.ForeignKey(
        Employees, models.DO_NOTHING, db_column='Employee_id')
    # Field name made lowercase.
    vehicle = models.ForeignKey(
        'Vehicles', models.DO_NOTHING, db_column='Vehicle_id')
    # Field name made lowercase.
    assignment_time = models.DateTimeField(
        db_column='Assignment_Time', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Order_Assignment'


class OrderItems(models.Model):
    # This table also has a composite primary key in SQL.
    # We'll tell Django that 'order' is the key for ORM purposes.
    # Field name made lowercase.
    order = models.OneToOneField(
        'Orders', models.DO_NOTHING, db_column='Order_id', primary_key=True)
    # Field name made lowercase.
    item = models.ForeignKey(MenuItems, models.DO_NOTHING, db_column='Item_id')
    # Field name made lowercase.
    quantity = models.IntegerField(db_column='Quantity')

    class Meta:
        managed = False
        db_table = 'Order_Items'
        unique_together = (('order', 'item'),)  # Represents the composite key


class Orders(models.Model):
    # Field name made lowercase.
    order_id = models.IntegerField(db_column='Order_id', primary_key=True)
    # Field name made lowercase.
    customer = models.ForeignKey(
        Customers, models.DO_NOTHING, db_column='Customer_id')
    # Field name made lowercase.
    restaurant = models.ForeignKey(
        'Restaurants', models.DO_NOTHING, db_column='Restaurant_id')
    # Field name made lowercase.
    payment = models.ForeignKey(
        'PaymentMethods', models.DO_NOTHING, db_column='Payment_id')
    # Field name made lowercase.
    total_price = models.DecimalField(
        db_column='Total_Price', max_digits=10, decimal_places=2)
    # Added Order_Date field based on your 'my_orders' page requirement
    order_date = models.DateTimeField(
        db_column='Order_Date', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Orders'

    def __str__(self):
        return f"Order #{self.order_id} by {self.customer.first_name}"


class PaymentMethods(models.Model):
    # Field name made lowercase.
    payment_id = models.IntegerField(db_column='Payment_id', primary_key=True)
    # Field name made lowercase.
    customer = models.ForeignKey(
        Customers, models.DO_NOTHING, db_column='Customer_id')
    # Field name made lowercase.
    total_spend = models.DecimalField(
        db_column='Total_Spend', max_digits=10, decimal_places=2, blank=True, null=True)
    # Field name made lowercase.
    payment_type = models.CharField(db_column='Payment_type', max_length=20)

    class Meta:
        managed = False
        db_table = 'Payment_Methods'
        verbose_name_plural = "Payment Methods"

    def __str__(self):
        return f"{self.payment_type} (ID: {self.payment_id})"


class Restaurants(models.Model):
    # Field name made lowercase.
    restaurant_id = models.IntegerField(
        db_column='Restaurant_id', primary_key=True)
    # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=100)
    # Field name made lowercase.
    address = models.ForeignKey(
        Address, models.DO_NOTHING, db_column='Address_id')
    # Field name made lowercase.
    cuisine = models.CharField(
        db_column='Cuisine', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Restaurants'
        verbose_name_plural = "Restaurants"

    def __str__(self):
        return self.name


class Vehicles(models.Model):
    # Field name made lowercase.
    vehicle_id = models.IntegerField(db_column='Vehicle_id', primary_key=True)
    # Field name made lowercase.
    registration_number = models.CharField(
        db_column='Registration_number', unique=True, max_length=20)
    # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=10)

    class Meta:
        managed = False
        db_table = 'Vehicles'
        verbose_name_plural = "Vehicles"

    def __str__(self):
        return f"{self.registration_number} ({self.type})"
