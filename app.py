from flask import Flask, render_template, jsonify, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    try:
        conn = sqlite3.connect('store.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception:
        print("Error connecting to database")
        return None

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Sorry, there is a server problem :("})
        brands = conn.execute('SELECT DISTINCT brand_name FROM Product ORDER BY brand_name').fetchall()
        return render_template('index.html', brands=brands)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        if conn:
            conn.close()

@app.route('/search_brand', methods=['POST'])
def search_brand():
    try:
        brand = request.form.get('brand')
        if not brand:
            return redirect(url_for('index'))
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Sorry, there is a server problem :("})

        results = conn.execute('''
            SELECT
                p.brand_name AS Brand,
                p.model AS Model,
                an.attribute_name AS AttributeName,
                av.attribute_value AS AttributeValue,
                po.quantity AS Quantity,
                po.wholesale_price AS WholesalePrice,
                po.sale_price AS SalePrice,
                MAX(pc.code_id) AS PromoCode
            FROM
                Product p
            JOIN
                ProductOption po ON p.product_id = po.product_PO_id
            LEFT JOIN
                ProductAttribute pa ON po.barcode_id = pa.barcode_PA_id
            LEFT JOIN
                AttributeName an ON pa.attribute_name_id = an.attribute_name_id
            LEFT JOIN
                AttributeValue av ON pa.attribute_value_id = av.attribute_value_id
            LEFT JOIN
                SaleItem si ON po.barcode_id = si.barcode_SI_id
            LEFT JOIN
                Sale s ON si.sale_SI_id = s.sale_id
            LEFT JOIN
                PromoCode pc ON s.code_S_id = pc.code_id
            WHERE p.brand_name = ?
            GROUP BY
                p.brand_name, p.model, an.attribute_name, av.attribute_value,
                po.quantity, po.wholesale_price, po.sale_price
            ORDER BY
                p.brand_name, p.model;
        ''', (brand,)).fetchall()

        return render_template('search_results.html', results=results, brand=brand)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        if conn:
            conn.close()

@app.route('/api/top_products')
def top_products():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Sorry, there is a server problem :("})

        products = conn.execute('''
            SELECT
                p.brand_name AS Brand,
                p.model AS Model,
                SUM(si.quantity_sold) AS TotalQuantitySold
            FROM
                SaleItem si
            JOIN
                ProductOption po ON si.barcode_SI_id = po.barcode_id
            JOIN
                Product p ON po.product_PO_id = p.product_id
            GROUP BY
                p.product_id, p.brand_name, p.model
            ORDER BY
                TotalQuantitySold DESC
            LIMIT 5
        ''').fetchall()

        profit = conn.execute('''
            SELECT
                SUM((po.sale_price - po.wholesale_price) * si.quantity_sold) AS profit
            FROM
                SaleItem si
            JOIN
                ProductOption po ON si.barcode_SI_id = po.barcode_id
        ''').fetchone()

        return jsonify({
            'products': [dict(row) for row in products],
            'profit': profit['profit'] / 100
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        if conn:
            conn.close()

@app.route('/api/top_categories')
def top_categories():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Sorry, there is a server problem :("})

        categories = conn.execute('''
            SELECT
                pc.category_name AS Category,
                COUNT(p.product_id) AS NumberOfProducts,
                SUM(si.quantity_sold) AS TotalQuantitySold
            FROM
                ProductCategory pc
            JOIN
                Product p ON pc.category_id = p.category_P_id
            JOIN
                ProductOption po ON p.product_id = po.product_PO_id
            JOIN
                SaleItem si ON po.barcode_id = si.barcode_SI_id
            GROUP BY
                pc.category_id, pc.category_name
            ORDER BY
                TotalQuantitySold DESC
            LIMIT 5
        ''').fetchall()

        revenue = conn.execute('''
            SELECT
                SUM(po.sale_price * si.quantity_sold) AS revenue
            FROM
                SaleItem si
            JOIN
                ProductOption po ON si.barcode_SI_id = po.barcode_id
        ''').fetchone()

        return jsonify({
            'categories': [dict(row) for row in categories],
            'revenue': revenue['revenue'] / 100
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        if conn:
            conn.close()

@app.route('/api/product_details')
def product_details():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Sorry, there is a server problem :("})

        products = conn.execute('''
            SELECT
                p.brand_name AS Brand,
                p.model AS Model,
                po.sale_price AS SalePrice,
                SUM(si.quantity_sold) AS TotalQuantitySold,
                ((po.sale_price - po.wholesale_price) * 100.0 / po.sale_price) AS MarginPercentage,
                s.supplier_name AS SupplierName,
                s.phone_number AS Phone,
                s.address AS Address
            FROM
                SaleItem si
            JOIN
                ProductOption po ON si.barcode_SI_id = po.barcode_id
            JOIN
                Product p ON po.product_PO_id = p.product_id
            JOIN
                ProductSupplier ps ON p.product_id = ps.product_PS_id
            JOIN
                Supplier s ON ps.supplier_PS_id = s.supplier_id
            GROUP BY
                p.product_id, p.brand_name, p.model, po.sale_price, po.wholesale_price,
                s.supplier_name, s.phone_number, s.address
            ORDER BY
                TotalQuantitySold DESC
        ''').fetchall()

        return jsonify([dict(row) for row in products])
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        if conn:
            conn.close()

@app.route('/api/category_details')
def category_details():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Sorry, there is a server problem :("})

        categories = conn.execute('''
            SELECT
                pc.category_name AS Category,
                COUNT(p.product_id) AS NumberOfProducts,
                SUM(si.quantity_sold) AS TotalQuantitySold,
                AVG(po.sale_price) AS AverageProductPrice,
                MAX(po.sale_price) AS MaximumProductPrice,
                SUM(si.price_sold_without_vat) AS TotalRevenue
            FROM
                ProductCategory pc
            JOIN
                Product p ON pc.category_id = p.category_P_id
            JOIN
                ProductOption po ON p.product_id = po.product_PO_id
            JOIN
                SaleItem si ON po.barcode_id = si.barcode_SI_id
            GROUP BY
                pc.category_id, pc.category_name
            ORDER BY
                TotalQuantitySold DESC
        ''').fetchall()

        return jsonify([dict(row) for row in categories])
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        if conn:
            conn.close()

@app.route('/api/chart-filters')
def get_chart_filters():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Sorry, there is a server problem :("})

        categories = conn.execute('''
            SELECT category_id, category_name
            FROM ProductCategory
            ORDER BY category_name
        ''').fetchall()

        return jsonify({
            'categories': [dict(row) for row in categories]
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        if conn:
            conn.close()

@app.route('/api/sales-data', methods=['POST'])
def get_sales_data():
    try:
        category_id = request.form.get('category_id')
        if not category_id:
            return jsonify({"error": "Category is required"})

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Sorry, there is a server problem :("})

        results = conn.execute('''
            SELECT
                s.sale_date AS SaleDate,
                p.category_P_id as category_id,
                SUM(si.quantity_sold) AS TotalQuantity,
                SUM(si.price_sold_without_vat) AS TotalSales
            FROM
                SaleItem si
            JOIN Sale s ON si.sale_SI_id = s.sale_id
            JOIN ProductOption po ON si.barcode_SI_id = po.barcode_id
            JOIN Product p ON po.product_PO_id = p.product_id
            WHERE p.category_P_id = ?
            GROUP BY
                s.sale_date, p.category_P_id
            ORDER BY
                s.sale_date
        ''', (category_id,)).fetchall()

        return jsonify([{
            'date': row['SaleDate'],
            'quantity': row['TotalQuantity'],
            'sales': row['TotalSales'] / 100
        } for row in results])
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        if conn:
            conn.close()



@app.route('/add_sale', methods=['POST'])
def add_sale():
    brand = request.form.get('brand')
    model = request.form.get('model')
    quantity_str = request.form.get('quantity')
    if not brand or not model or not quantity_str:
        return jsonify({"error": "Please fill in all required fields"})
    if not quantity_str.isdigit():
        return jsonify({"error": "Quantity must be a number"})
    quantity = int(quantity_str)
    conn = None
    try:
        conn = sqlite3.connect('store.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT po.barcode_id, po.quantity, po.sale_price
            FROM Product p
            JOIN ProductOption po ON p.product_id = po.product_PO_id
            WHERE p.brand_name = ? AND p.model = ?
        ''', (brand, model))
        product = cursor.fetchone()
        if not product:
            return jsonify({"error": "Product not found"})
        if product['quantity'] < quantity:
            return jsonify({"error": "Not enough stock"})
        cursor.execute('''
            UPDATE ProductOption
            SET quantity = quantity - ?
            WHERE barcode_id = ?
        ''', (quantity, product['barcode_id']))
        cursor.execute('''
            INSERT INTO Sale (sale_date, source_name, tax_rate)
            VALUES (datetime('now'), 'Manual Entry', 20)
        ''')
        sale_id = cursor.lastrowid
        cursor.execute('''
            INSERT INTO SaleItem (sale_SI_id, barcode_SI_id, quantity_sold, price_sold_without_vat)
            VALUES (?, ?, ?, ?)
        ''', (sale_id, product['barcode_id'], quantity, product['sale_price']))
        conn.commit()
        return jsonify({"success": "Sale recorded successfully"})
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        if conn:
            conn.close()



@app.route('/change_price', methods=['POST'])
def change_price():
    brand = request.form.get('brand')
    model = request.form.get('model')
    new_price_str = request.form.get('new_price')
    if not brand or not model or not new_price_str:
        return jsonify({"error": "Please fill in all required fields"})
    if not new_price_str.isdigit():
        return jsonify({"error": "Price must be a number"})
    new_price = int(new_price_str)
    conn = None
    try:
        conn = sqlite3.connect('store.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT po.barcode_id, po.sale_price
            FROM Product p
            JOIN ProductOption po ON p.product_id = po.product_PO_id
            WHERE p.brand_name = ? AND p.model = ?
        ''', (brand, model))
        product = cursor.fetchone()
        if not product:
            return jsonify({"error": "Product not found"})
        cursor.execute('''
            UPDATE ProductOption
            SET sale_price = ?
            WHERE barcode_id = ?
        ''', (new_price, product['barcode_id']))
        cursor.execute('''
            INSERT INTO PriceHistory (barcode_PH_id, old_price, new_price, change_date)
            VALUES (?, ?, ?, datetime('now'))
        ''', (product['barcode_id'], product['sale_price'], new_price))
        conn.commit()
        return jsonify({"success": "Price updated successfully"})
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    app.run(debug=True)