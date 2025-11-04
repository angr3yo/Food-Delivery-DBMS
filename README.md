# 🍴 Food Delivery DBMS (Django + MySQL)

A full-stack **Food Delivery Management System** built using **Django**, **MySQL**, and **Bootstrap**, designed to simulate a real-world food ordering platform.  
This project integrates restaurants, customers, orders, and delivery management into one cohesive system with database triggers, procedures, and foreign key relationships.

---

## 🚀 Features

### 👤 Customer Side
- User registration and login  
- Browse restaurants and menu items  
- Add items to cart and place orders  
- Select preferred payment method (Cash, Card, UPI, etc.)  
- View order confirmation and driver assignment details  

### 🍽️ Restaurant Management
- Add, edit, and manage restaurant menus  
- Track orders and sales  
- Monitor total spends from different payment types  

### 🚗 Delivery System
- Dynamic driver assignment using SQL **stored procedures**  
- Vehicle and driver information displayed upon confirmation  

### 💳 Payment System
- Secure payment tracking through `Payment_Methods` table  
- Supports multiple payment types per customer  
- Automatically updates `total_spend` on each order  

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

## 🗄️ Database Schema Overview

### Key Tables:
- `Customers`
- `Restaurants`
- `Menu_Items`
- `Orders`
- `Order_Items`
- `Payment_Methods`
- `Employees`
- `Vehicles`
- `Order_Assignment`

### Highlights:
- **Triggers** and **Stored Procedures**:
  - `AssignOrderDriver` → Assigns a random driver & vehicle for every new order  
  - Enforces referential integrity with **foreign keys**
- **Unique constraints** for `(Customer, Payment_type)` to prevent duplicates  

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

`git clone https://github.com/angr3yo/Food-Delivery-DBMS.git
cd Food-Delivery-DBMS/fooddelivery_project`

2️⃣ Create & activate virtual environment
`python3 -m venv venv
source venv/bin/activate     # (Mac/Linux)
venv\Scripts\activate        # (Windows)`

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
`python manage.py migrate
python manage.py runserver`


Then visit: 👉 http://127.0.0.1:8000/



🧩 Folder Structure
`fooddelivery_project/
│
├── core/                     # Main Django app (views, models, urls)
├── templates/                # HTML templates
├── static/                   # CSS, JS, images
├── manage.py
├── requirements.txt
└── README.md`

🧑‍💻 Author

`Nithya Gauri 
Pooja Viswanathan
📍 PES University`


🪪 License

This project is open source under the MIT License.
Feel free to use, modify, and distribute with attribution.
