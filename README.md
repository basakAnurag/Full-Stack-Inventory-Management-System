# Inventory Management System

## Description

This project is a web-based **Inventory Management System** built using Python, Flask, and SQLite.

It provides an intuitive browser interface for two types of users:

* **Customers** – view and purchase products
* **Sellers** – manage store inventory

The system securely manages user sessions and records **purchase history** to track all inventory transactions.

## Features

* Web-based interface built with HTML, CSS, and Jinja2 templates
* User authentication and session management (register/login/logout)
* Two user roles: **Customer** and **Seller**
* Product inventory management
* Product purchasing system
* Purchase history tracking
* Low stock warnings
* SQLite database storage with automatic initialization^^

## Database Structure

The system uses an SQLite database (`A3_04_4_1_85.db`) with three tables. The database and tables are generated automatically upon the first run.

### Users Table

Stores login credentials and roles.

| **Field** | **Type** | **Description** |
| --------------- | -------------- | --------------------- |
| id              | INTEGER        | Primary key           |
| username        | TEXT           | Unique username       |
| password_hash   | TEXT           | Hashed password       |
| role            | TEXT           | customer or seller    |
| created_at      | TEXT           | Account creation time |

### Products Table

Stores product information.

| **Field** | **Type** | **Description** |
| --------------- | -------------- | --------------------- |
| id              | INTEGER        | Product ID            |
| name            | TEXT           | Product name          |
| price           | REAL           | Product price         |
| stock           | INTEGER        | Quantity available    |

### Purchase History Table

Records every purchase made by customers.

| **Field** | **Type** | **Description**     |
| --------------- | -------------- | ------------------------- |
| id              | INTEGER        | Transaction ID            |
| user_id         | INTEGER        | Customer ID               |
| username        | TEXT           | Customer username         |
| product_id      | INTEGER        | Product ID                |
| product_name    | TEXT           | Product purchased         |
| quantity        | INTEGER        | Quantity bought           |
| total_price     | REAL           | Total purchase cost       |
| purchase_date   | TEXT           | Date and time of purchase |

## Customer Functions

Customers have access to a dedicated dashboard where they can:

1. **Register or login** to their secure session
2. **View available products** (items out of stock are hidden)
3. **Purchase products** by specifying a valid quantity
4. **View personal purchase history** sorted by date

When a product is purchased:

* Product stock is immediately updated in the database
* A detailed purchase history record is created

## Seller Functions

Sellers have access to an inventory management dashboard where they can:

1. **Register or login** to their secure session
2. **View full inventory** , including low-stock warnings
3. **Add new products** to the store
4. **Update product price or stock**
5. **Delete products** entirely from the database

## How to Run

### 1. Clone the repository

**Bash**

```
git clone <repository_url>
cd inventory-system
```

### 2. Install requirements

The backend relies on Flask; all other modules (SQLite3, Hashlib, Datetime) use Python's standard library.

**Bash**

```
pip install -r requirements.txt
```

### 3. Run the application

Start the Flask development server:

**Bash**

```
python app.py
```

### 4. Access the Web App

Open your preferred web browser and navigate to:

**Plaintext**

```
http://127.0.0.1:5000
```

## Example Workflow

**Seller:**

1. Access the web app and register/login as a  **seller** .
2. From the Seller Dashboard, use the "Add New Product" form.
3. Manage inventory by updating prices/stock or deleting old items.

**Customer:**

1. Access the web app and register/login as a  **customer** .
2. Browse the "Available Products" table on the Customer Dashboard.
3. Enter a quantity and click "Buy" on a desired item.
4. Scroll down to review your "Purchase History".

## Technologies Used

* Python (Backend Logic)
* Flask (Web Framework & Routing)
* SQLite3 (Database Storage)
* HTML5 & CSS3 (Frontend Styling & Structure)
* Jinja2 (Dynamic Template Rendering)

## Author

Anurag
