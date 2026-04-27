<img width="1280" height="811" alt="photo_2026-04-27_02-55-33" src="https://github.com/user-attachments/assets/b485ff7a-b980-48a5-95fa-bfb9ecaaacca" />
<img width="1280" height="451" alt="photo_2026-04-27_02-55-33 (2)" src="https://github.com/user-attachments/assets/dc56b838-0aff-4693-b44b-1cbba71fbf87" />
[assignment1(DB).pdf](https://github.com/user-attachments/files/27121159/assignment1.DB.pdf)
[assignment2(normalization).pdf](https://github.com/user-attachments/files/27121170/assignment2.normalization.pdf)

# Electronics Store Dashboard 

## Project Essence

This project is the final phase of a Database course(CMPS244). The main goal is to build a functional web application that interacts with a complex relational database. It simulates a real-world electronics store management system where you can track inventory, sales, suppliers, and price changes.

The application provides a "Dashboard" view to help managers see how the business is performing. It includes data visualization, search capabilities, and tools to update the database.

## Tech Stack

- **Backend:** Python 3 with **Flask**.
- **Database:** **SQLite3**. A relational database used to store products, categories, sales, and more.
- **Frontend:** Standard **HTML5**, **CSS3**, and **JavaScript**.
- **Data Visualization:** **Apache ECharts** library is used to generate dynamic line charts for sales trends.

## Detailed Functionality

### 1. Business Analytics 
- **Top 5 Selling Products:** A table showing the most popular items based on quantity sold.
- **Top 5 Selling Categories:** Displays which product categories generate the most volume.
- **Financial Metrics:** Real-time calculation of **Total Profit** and **Total Revenue** across all sales.
- **Sales Trends:** A dynamic line chart that shows daily sales and quantity sold. You can filter this chart by specific product categories.

### 2. Product & Inventory Management
- **Brand Search:** A dedicated search feature to find all products belonging to a specific brand.
- **Product Details:** View comprehensive info including brand, model, price, margin percentage, and supplier contact details.
- **Category Statistics:** Breakdown of each category with product counts, average prices, and maximum prices.
- **Inventory Updates:** A functional form to record new sales, which automatically reduces the stock quantity in the database.
- **Price Management:** A feature to change product prices. When a price is updated, the system logs the old price in a `PriceHistory` table for tracking.

### 3. Database Architecture
The project uses a structured relational database with the following key tables:
- **Product & Category:** Defines the catalog of items.
- **ProductOption & Attributes:** Handles different versions of products using EAV-like attributes.
- **Sales & SaleItems:** Tracks every transaction, including dates, sources(Online/Store), and quantities.
- **Suppliers:** Stores contact information for tech providers.
- **PriceHistory:** Keeps a record of every price change for audit purposes.
- **Performance:** Database indexes are implemented on frequently searched columns to ensure the app stays fast even with thousands of records.

## Setup & Installation

### Prerequisites
- Python 3.x installed on your system.

### Steps
1. **Clone the Project**
   ```bash
   git clone https://github.com/AdagamovNikita/Dashboard.git
   cd Dashboard
   ```
2. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```
3. **Initialize the Database**
   Run the setup script to create the `store.db` file and populate it with 1500+ sample sales records.
   ```bash
   python init_db.py
   ```
4. **Run the App**
   ```bash
   python app.py
   ```
5. **Access the Dashboard**
   Open your browser and go to `http://127.0.0.1:5000`.

---
*Created for CMPS244 - Database Systems.*
