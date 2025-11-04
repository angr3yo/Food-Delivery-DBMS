# 🍴 Food Delivery DBMS (Django + MySQL)

A full-stack **Food Delivery Management System** built using **Django**, **MySQL**, and **Bootstrap**, designed to simulate a real-world food ordering platform.  
This project integrates restaurants, customers, orders, and delivery management into one cohesive system with database triggers, procedures, and foreign key relationships.

---

## 🚀 Features

### 🧍 **User & Customer Management**
- `auth_user` used for login/signup.
- Linked `Customers` table for user profile (phone, DOB, gender).
- `Customer_Addresses` allows multiple addresses per user.
### 🍴 **Restaurant and Menu**
- `Restaurants` linked to `Address` for location.
- `Menu_Items` mapped to restaurants via `Restaurant_id`.
- Supports multiple cuisines, dynamic pricing, and categories.

### 🛒 **Order Workflow**
- Orders are placed by customers for a single restaurant.
- `Order_Items` joins `Orders` with `Menu_Items` to capture quantity and price.
- Total price recalculated automatically via triggers or Django ORM logic.

### 💳 **Payment System**
- `Payment_Methods` stores customer payment preferences (UPI, Card, or Cash).
- Tracks `Total_Spend` for each customer and payment type.
- Automatically updated after every successful order. 
- Supports multiple payment types per customer  
  
### 🚚 **Delivery Assignment**
- `Employees` table stores staff info (drivers, managers).
- `Vehicles` stores vehicle type (bike, EV, etc.) and registration.
- `Order_Assignment` links each order to a driver and vehicle.
### 🚗 Delivery System
- Dynamic driver assignment using SQL **stored procedures**  
- Vehicle and driver information displayed upon confirmation  

<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/aa932004-37cb-4a63-a145-822e0706e572" />
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/06c426ca-03ff-4709-b1e5-4c7e0bbd4b24" />
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/f96585e5-4bd1-4a16-9b12-4bc01219586f" />
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/c36b26d0-f326-4ce6-9018-7793db8e22da" />
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/c284b2af-e3ac-4b58-bdaa-351f39aba28a" />
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/1fba64fa-dcae-445a-814e-76e871198d10" />
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/19c850f2-20a3-404d-b2c0-2c637de8adb0" />

 
<img width="2940" height="1912" alt="image" src="https://github.com/user-attachments/assets/749462c3-a36e-4652-adb9-72e808fe619c" />




---

## 🧠 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | HTML, CSS, Bootstrap |
| **Backend** | Django (Python 3.13) |
| **Database** | MySQL |
| **ORM** | Django Models (connected to MySQL tables) |
| **Version Control** | Git + GitHub |

---

## 🗄️ Database: `FoodDelivery`

### 📦 Main Tables Overview

| Table | Description |
|--------|-------------|
| **auth_user** | Default Django user table (login credentials and permissions) |
| **Customers** | Stores customer details linked to `auth_user` |
| **Customer_Addresses** | Customer delivery addresses (FK to `Customers`) |
| **Restaurants** | Registered restaurants with cuisine type and location |
| **Menu_Items** | Menu items offered by restaurants with price and category |
| **Orders** | Customer orders containing total price, status, and payment |
| **Order_Items** | Items within each order (with quantity and price mapping) |
| **Payment_Methods** | Tracks payment type (UPI/Card/Cash) and total spend per customer |
| **Employees** | Staff members, including delivery drivers |
| **Vehicles** | Vehicles assigned to employees for order delivery |
| **Order_Assignment** | Maps orders to assigned employees and vehicles |
| **Address** | Stores location details (used for restaurants/customers) |


### Highlights:
## 🔁 Triggers, Procedures, and Functions (Database Automation)

### ⚙️ Stored Triggers

| Trigger | Purpose |
|----------|----------|
| **trg_UpdateTotalSpend_AfterOrderUpdate** | Automatically updates `Payment_Methods.Total_Spend` after each successful order |
| **trg_ValidateOrderItemRestaurant** | Prevents items from multiple restaurants being added to one order |
| **trg_AutoTimestamp_OrderAssignment** | Automatically sets `Assignment_Time` when an order is assigned to a driver |

---

### 🧮 Stored Procedures

| Procedure | Purpose |
|------------|----------|
| **AssignOrderDriver(order_id INT, driver_id INT)** | Assigns a driver and corresponding vehicle to a given order |
| **sp_RecalcOrderTotal(order_id INT)** | Recalculates total order price using `Order_Items` and updates `Orders.Total_Price` |
| **sp_UpdateCustomerSpend(customer_id INT)** | Updates `Payment_Methods.Total_Spend` for a customer after each completed payment |

---

### 🧠 SQL Functions

| Function | Returns | Purpose |
|-----------|----------|----------|
| **fn_GetRestaurantRevenue(restaurant_id INT)** | `DECIMAL(10,2)` | Calculates total revenue earned by a specific restaurant |
| **fn_GetCustomerTotalSpend(customer_id INT)** | `DECIMAL(10,2)` | Returns total spend of a given customer across all payment types |
| **fn_GetAverageDeliveryTime(driver_id INT)** | `INT` (minutes) | Calculates average delivery time handled by a driver |
| **fn_GetOrderItemCount(order_id INT)** | `INT` | Returns total number of items within a specific order |
| **fn_CalculateDiscount(total DECIMAL(10,2))** | `DECIMAL(10,2)` | Applies conditional discount logic (e.g., 10% off if total > ₹500) |

---

🧩 *These database-level automations help maintain data integrity, enforce business rules, and keep analytics real-time without extra Django overhead.*

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

`git clone https://github.com/angr3yo/Food-Delivery-DBMS.git  `
`cd Food-Delivery-DBMS/fooddelivery_project`

2️⃣ Create & activate virtual environment
`python3 -m venv venv`
`source venv/bin/activate     # (Mac/Linux)`
`venv\Scripts\activate        # (Windows)`

3️⃣ Install dependencies
`pip install -r requirements.txt`

4️⃣ Configure database connection

In settings.py, update:

`DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'FoodDelivery',
        'USER': 'root',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}`

5️⃣ Run migrations and start the server
`python manage.py migrate`
\n`python manage.py runserver`


Then visit: 👉 http://127.0.0.1:8000/




🧑‍💻 Authors

`Nithya Gauri` 
`Pooja Viswanathan`
`📍 PES University`


🪪 License

This project is open source under the MIT License.
Feel free to use, modify, and distribute with attribution.
