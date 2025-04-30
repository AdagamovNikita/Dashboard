from flask import Flask, render_template, jsonify, request, redirect, url_for
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from init_db import Base, Product, ProductCategory, ProductOption, AttributeName, AttributeValue, ProductAttribute, Sale, SaleItem, Supplier, ProductSupplier, PromoCode, PriceHistory



app = Flask(__name__)
engine = create_engine('sqlite:///store.db') #just a connection to a database
DBSession = sessionmaker(bind = engine) #other name as we have Session in init_db but the functionality is the same



def get_db_session():
    try:
        session = DBSession()
        return session
    except Exception as  e:
        print(f"Error: {e}")
        return None


#so, for the backend I used our lectures about the Flask as a reference. And for the final phase I just rewrite absolutely the same but with orm
@app.route('/') #homepage
def index():
    session = get_db_session()
    if not session:
        return jsonify({"error": "Sorry, there is a server problem :( "})
    try:
        brands = session.query( #it provides all brands for the dropdown menu
            Product.brand_name
        ).distinct(
        ).order_by(
            Product.brand_name
        ).all() 
        return render_template('index.html',brands=brands) #returns the index.html with all brands
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        session.close()



@app.route('/search_brand',methods=['POST'])
def search_brand():
    brand = request.form.get('brand')
    if not brand:
        return redirect(url_for('index')) #if no brands, it sends users to homepage
    session = get_db_session()
    if not session:
        return jsonify({"error": "Sorry, there is a server problem :("})
    try:
        results = session.query(
            Product.brand_name.label('Brand'),
            Product.model.label('Model'),
            AttributeName.attribute_name.label('AttributeName'),
            AttributeValue.attribute_value.label('AttributeValue'),
            ProductOption.quantity.label('Quantity'),
            ProductOption.wholesale_price.label('WholesalePrice'),
            ProductOption.sale_price.label('SalePrice'),
            func.max(PromoCode.code_id).label('PromoCode')
        ).join(
            ProductOption, Product.product_id == ProductOption.product_PO_id
        ).outerjoin(
            ProductAttribute,ProductOption.barcode_id == ProductAttribute.barcode_PA_id
        ).outerjoin(
            AttributeName,ProductAttribute.attribute_name_id == AttributeName.attribute_name_id
        ).outerjoin(
            AttributeValue,ProductAttribute.attribute_value_id == AttributeValue.attribute_value_id
        ).outerjoin(
            SaleItem, ProductOption.barcode_id == SaleItem.barcode_SI_id
        ).outerjoin(
            Sale, SaleItem.sale_SI_id == Sale.sale_id
        ).outerjoin(
            PromoCode, Sale.code_S_id == PromoCode.code_id
        ).filter(
            Product.brand_name == brand
        ).group_by(
            Product.brand_name, Product.model,
            AttributeName.attribute_name,AttributeValue.attribute_value,
            ProductOption.quantity, ProductOption.wholesale_price, ProductOption.sale_price
        ).order_by(
            Product.brand_name, Product.model
        ).all()
        return render_template('search_results.html', results = results, brand = brand)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        session.close()



@app.route('/api/top_products')
def top_products():
    session = get_db_session()
    if not session:
        return jsonify({"error": "Sorry, there is a server problem :("})
    try:
        products = session.query(
            Product.brand_name.label('Brand'),
            Product.model.label('Model'),
            func.sum(SaleItem.quantity_sold).label('TotalQuantitySold')
        ).join(
            ProductOption, SaleItem.barcode_SI_id == ProductOption.barcode_id
        ).join(
            Product, ProductOption.product_PO_id == Product.product_id
        ).group_by(
            Product.product_id, Product.brand_name, Product.model
        ).order_by(
            func.sum(SaleItem.quantity_sold).desc()
        ).limit(5).all()
        profit = session.query(
            func.sum((ProductOption.sale_price - ProductOption.wholesale_price) * SaleItem.quantity_sold).label('profit')
        ).join(
            ProductOption, SaleItem.barcode_SI_id == ProductOption.barcode_id
        ).first()
        #I have to manually convert each sqlalchemy row object to a dictionary, put this dictionary into the list and send this list to Flask's jsonify() function can convert it to JSON
        #It was not obvious and we did not have this material in the lectures, so I had to use help from reddit and chatgpt for this
        products_list = []
        for row in products:
            products_list.append({
                'Brand': row.Brand,
                'Model': row.Model,
                'TotalQuantitySold': row.TotalQuantitySold
            })
        return jsonify({ #and now Flask's jsonify() function can convert it to JSON
            'products': products_list,
            'profit': profit[0] / 100 #I decided to store everything related to money in cents instead of euros and then divide by 100 for display
        })
    except Exception as e:
        print(f"Error: {e}")
        return  jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        session.close()



@app.route('/api/top_categories')
def top_categories():
    session=get_db_session()
    if not session:
        return jsonify({"error": "Sorry, there is a server problem :( "})
    try:
        categories = session.query(
            ProductCategory.category_name.label('Category'),
            func.count(Product.product_id).label('NumberOfProducts'),
            func.sum(SaleItem.quantity_sold).label('TotalQuantitySold')
        ).join(
            Product,ProductCategory.category_id == Product.category_P_id
        ).join(
            ProductOption,Product.product_id == ProductOption.product_PO_id
        ).join(
            SaleItem,ProductOption.barcode_id== SaleItem.barcode_SI_id
        ).group_by(
            ProductCategory.category_id, ProductCategory.category_name
        ).order_by(
            func.sum(SaleItem.quantity_sold).desc()
        ).limit(5).all()
        revenue = session.query(
            func.sum(ProductOption.sale_price * SaleItem.quantity_sold).label('revenue')
        ).join(
            SaleItem, SaleItem.barcode_SI_id == ProductOption.barcode_id
        ).first()
        #same approach
        categories_list = []
        for row in categories:
            categories_list.append({
                'Category': row.Category,
                'NumberOfProducts': row.NumberOfProducts,
                'TotalQuantitySold': row.TotalQuantitySold
            })
        return jsonify({
            'categories': categories_list,
            'revenue': revenue[0] / 100 #same logic
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :( "})
    finally:
        session.close()



@app.route('/api/product_details')
def product_details():
    session=get_db_session()
    if not session:
        return jsonify({"error": "Sorry, there is a server problem :("})
    try:
        products = session.query(
            Product.brand_name.label('Brand'),
            Product.model.label('Model'),
            ProductOption.sale_price.label('SalePrice'),
            func.sum(SaleItem.quantity_sold).label('TotalQuantitySold'),
            ((ProductOption.sale_price - ProductOption.wholesale_price)*100.0 / ProductOption.sale_price).label('MarginPercentage'),
            Supplier.supplier_name.label('SupplierName'),
            Supplier.phone_number.label('Phone'),
            Supplier.address.label('Address')
        ).join(
            ProductOption,Product.product_id == ProductOption.product_PO_id
        ).join(
            SaleItem,ProductOption.barcode_id == SaleItem.barcode_SI_id
        ).join(
            ProductSupplier,Product.product_id == ProductSupplier.product_PS_id
        ).join(
            Supplier,ProductSupplier.supplier_PS_id == Supplier.supplier_id
        ).group_by(
            Product.product_id,Product.brand_name, Product.model,
            ProductOption.sale_price, ProductOption.wholesale_price,
            Supplier.supplier_name,Supplier.phone_number, Supplier.address
        ).order_by(
            func.sum(SaleItem.quantity_sold).desc()
        ).all()
        #same approach
        products_list = []
        for row in products:
            products_list.append({
                'Brand': row.Brand,
                'Model': row.Model,
                'SalePrice': row.SalePrice,
                'TotalQuantitySold': row.TotalQuantitySold,
                'MarginPercentage': row.MarginPercentage,
                'SupplierName': row.SupplierName,
                'Phone': row.Phone,
                'Address': row.Address
            })
        return jsonify(products_list)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        session.close()



@app.route('/api/category_details')
def category_details():
    session=get_db_session()
    if not session:
        return jsonify({"error": "Sorry, there is a server problem :("})
    try:
        categories = session.query(
            ProductCategory.category_name.label('Category'),
            func.count(Product.product_id).label('NumberOfProducts'),
            func.sum(SaleItem.quantity_sold).label('TotalQuantitySold'),
            func.avg(ProductOption.sale_price).label('AverageProductPrice'),
            func.max(ProductOption.sale_price).label('MaximumProductPrice'),
            func.sum(SaleItem.price_sold_without_vat).label('TotalRevenue')
        ).join(
            Product,ProductCategory.category_id == Product.category_P_id
        ).join(
            ProductOption,Product.product_id == ProductOption.product_PO_id
        ).join(
            SaleItem,ProductOption.barcode_id == SaleItem.barcode_SI_id
        ).group_by(
            ProductCategory.category_id,ProductCategory.category_name
        ).order_by(
            func.sum(SaleItem.quantity_sold).desc()
        ).all()
        #same approach
        categories_list = []
        for row in categories:
            categories_list.append({
                'Category': row.Category,
                'NumberOfProducts': row.NumberOfProducts,
                'TotalQuantitySold': row.TotalQuantitySold,
                'AverageProductPrice': row.AverageProductPrice,
                'MaximumProductPrice': row.MaximumProductPrice,
                'TotalRevenue': row.TotalRevenue
            })
        return jsonify(categories_list)
    except Exception as e:
        print(f"Error:{e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        session.close()



@app.route('/api/chart-filters')
def get_chart_filters():
    session=get_db_session()
    if not session:
        return jsonify({"error": "Sorry, there is a server problem :("})
    try:
        categories =session.query(
            ProductCategory.category_id,
            ProductCategory.category_name
        ).order_by(
            ProductCategory.category_name
        ).all()
        #same approach
        categories_list = []
        for row in categories:
            categories_list.append({
                'category_id': row.category_id,
                'category_name': row.category_name
            })
        return jsonify({
            'categories': categories_list
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :( "})
    finally:
        session.close()



@app.route('/api/sales-data',methods=['POST'])
def get_sales_data():
    category_id=request.form.get('category_id')
    if not category_id:
        return jsonify({"error": "Category is required"})
    session=get_db_session()
    if not session:
        return jsonify({"error": "Sorry, there is a server problem :("})
    try:
        results= session.query(
            Sale.sale_date.label('SaleDate'),
            Product.category_P_id.label('category_id'),
            func.sum(SaleItem.quantity_sold).label('TotalQuantity'),
            func.sum(SaleItem.price_sold_without_vat).label('TotalSales')
        ).join(
            SaleItem,SaleItem.sale_SI_id == Sale.sale_id
        ).join(
            ProductOption,SaleItem.barcode_SI_id == ProductOption.barcode_id
        ).join(
            Product,ProductOption.product_PO_id == Product.product_id
        ).filter(
            Product.category_P_id == category_id
        ).group_by(
            Sale.sale_date,Product.category_P_id
        ).order_by(
            Sale.sale_date
        ).all()
        #same approach
        return jsonify([{
            'date': row.SaleDate,
            'quantity': row.TotalQuantity,
            'sales': row.TotalSales / 100 #same logic
        } for row in results])
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        session.close()



@app.route('/add_sale', methods=['POST'])
def add_sale():
    brand=request.form.get('brand')
    model=request.form.get('model')
    quantity_str = request.form.get('quantity')
    if not brand or not model or not quantity_str: #just data validation
        return jsonify({"error": "Please fill in all required fields"})
    if not quantity_str.isdigit():
        return jsonify({"error": "Quantity must be a number"})
    quantity = int(quantity_str)
    session=get_db_session()
    if not session:
        return jsonify({"error": "Sorry, there is a server problem :("})
    try:
        product_option = session.query(
            ProductOption
        ).join(
            Product,Product.product_id == ProductOption.product_PO_id
        ).filter(
            Product.brand_name == brand,
            Product.model == model
        ).first()
        if not product_option:
            return jsonify({"error": "Product not found"})
        if product_option.quantity < quantity:
            return jsonify({"error": "Not enough stock"})
        product_option.quantity -= quantity
        new_sale = Sale( #here we are creating a new sale record
            sale_date=datetime.now(),
            source_name='Manual Entry',
            tax_rate=20
        )
        session.add(new_sale)
        session.commit()
        new_sale_item = SaleItem( #here we are createing a new sale item record
            sale_SI_id=new_sale.sale_id,
            barcode_SI_id=product_option.barcode_id,
            quantity_sold=quantity,
            price_sold_without_vat=product_option.sale_price
        )
        session.add(new_sale_item)
        session.commit()
        return jsonify({"success": "Sale recorded sucessfully"})
    except Exception as e:
        session.rollback() #it cancel incomplete database changes when errors happen
        print(f"Error: {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        session.close()



@app.route('/change_price',methods=['POST'])
def change_price():
    brand=request.form.get('brand')
    model=request.form.get('model')
    new_price_str = request.form.get('new_price')
    if not brand or not model or not new_price_str:
        return jsonify({"error": "Please fill in all required fields"})
    if not new_price_str.isdigit():
        return jsonify({"error": "Price must be a number"})
    new_price = int(new_price_str)
    session=get_db_session()
    if not session:
        return jsonify({"error": "Sorry, there is a server problem :("})
    try:
        product_option = session.query(
            ProductOption
        ).join(
            Product, Product.product_id == ProductOption.product_PO_id
        ).filter(
            Product.brand_name == brand,
            Product.model == model
        ).first()
        if not product_option:
            return jsonify({"error": "Product not found"})
        price_history = PriceHistory(
            barcode_PH_id=product_option.barcode_id,
            old_price=product_option.sale_price,
            new_price=new_price,
            change_date=datetime.now()
        )
        session.add(price_history)
        product_option.sale_price = new_price
        session.commit()
        return jsonify({"success": "Price updated successfully"})
    except Exception as e:
        session.rollback()
        print(f"Error:  {e}")
        return jsonify({"error": "Sorry, there is a server problem :("})
    finally:
        session.close()



if __name__ == '__main__':
    app.run(debug=True)