from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
import random
import time
random.seed(time.time())



Base = declarative_base() #it creates a base class for other tables that I will use
engine = create_engine('sqlite:///store.db') #just a connection to a database 
Session = sessionmaker(bind=engine) #it is like cursor in raw sql



class ProductCategory(Base):
    __tablename__ = 'ProductCategory'
    category_id =Column(Integer, primary_key=True)
    category_name = Column(String, nullable=False)
    products = relationship('Product',  back_populates='category')



class Product(Base):
    __tablename__ = 'Product'
    product_id = Column(Integer,  primary_key=True)
    model = Column(String, nullable=False)
    category_P_id = Column(Integer, ForeignKey('ProductCategory.category_id'))
    brand_name= Column(String)
    category = relationship('ProductCategory', back_populates='products')
    options = relationship('ProductOption', back_populates='product')
    suppliers = relationship('ProductSupplier', back_populates='product')



class ProductOption(Base):
    __tablename__ = 'ProductOption'
    barcode_id = Column(String, primary_key= True)
    product_PO_id = Column(Integer, ForeignKey('Product.product_id'))
    quantity = Column(Integer,nullable=False)
    wholesale_price = Column(Integer, nullable=False)
    sale_price = Column(Integer, nullable=False)
    product = relationship('Product',  back_populates='options')
    attributes = relationship('ProductAttribute', back_populates='product_option')
    price_history = relationship('PriceHistory', back_populates='product_option')
    sale_items= relationship('SaleItem',back_populates='product_option')



class AttributeName(Base):
    __tablename__ = 'AttributeName'
    attribute_name_id = Column(Integer, primary_key=True)
    attribute_name = Column(String, nullable=False, unique=True)
    attributes = relationship('ProductAttribute', back_populates='attribute_name')



class AttributeValue(Base):
    __tablename__ = 'AttributeValue'
    attribute_value_id = Column(Integer, primary_key=True)
    attribute_value = Column(String, nullable=False, unique=True)
    attributes = relationship('ProductAttribute',  back_populates='attribute_value')



class ProductAttribute(Base):
    __tablename__ = 'ProductAttribute'
    barcode_PA_id = Column(String, ForeignKey('ProductOption.barcode_id'), primary_key=True)
    attribute_name_id = Column(Integer, ForeignKey('AttributeName.attribute_name_id'),  primary_key=True)
    attribute_value_id = Column(Integer, ForeignKey('AttributeValue.attribute_value_id'),primary_key=True)
    product_option= relationship('ProductOption', back_populates='attributes')
    attribute_name = relationship('AttributeName',back_populates='attributes')
    attribute_value = relationship('AttributeValue', back_populates='attributes')



class PriceHistory(Base):
    __tablename__ = 'PriceHistory'
    price_id = Column(Integer, primary_key=True)
    barcode_PH_id = Column(String, ForeignKey('ProductOption.barcode_id'))
    old_price = Column(Integer, nullable=False)
    new_price = Column(Integer,  nullable=False)
    change_date = Column(DateTime, nullable=False)
    product_option = relationship('ProductOption', back_populates ='price_history')



class Supplier(Base):
    __tablename__ = 'Supplier'
    supplier_id = Column(Integer, primary_key=True)
    supplier_name = Column(String,nullable=False)
    phone_number = Column(String)
    address = Column(String)
    products = relationship('ProductSupplier', back_populates='supplier')



class ProductSupplier(Base):
    __tablename__ = 'ProductSupplier'
    product_PS_id = Column(Integer, ForeignKey('Product.product_id'),primary_key=True)
    supplier_PS_id = Column(Integer, ForeignKey('Supplier.supplier_id'),primary_key=True)
    product = relationship('Product',  back_populates='suppliers')
    supplier = relationship('Supplier', back_populates='products')



class PromoCode(Base):
    __tablename__ = 'PromoCode'
    code_id = Column(String, primary_key=True)
    discount_percentage = Column(Integer, nullable=False)
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date,nullable=False)
    sales = relationship('Sale', back_populates='promo_code')



class Sale(Base):
    __tablename__ = 'Sale'
    sale_id = Column(Integer, primary_key=True)
    sale_date = Column(DateTime, nullable=False)
    source_name= Column(String)
    code_S_id= Column(String, ForeignKey('PromoCode.code_id'))
    tax_rate = Column(Integer)
    promo_code = relationship('PromoCode',  back_populates='sales')
    items = relationship('SaleItem', back_populates='sale')



class SaleItem(Base):
    __tablename__ = 'SaleItem'
    sale_item_id = Column(Integer, primary_key=True)
    sale_SI_id = Column(Integer,  ForeignKey('Sale.sale_id'))
    barcode_SI_id = Column(String, ForeignKey('ProductOption.barcode_id'), nullable=False)
    quantity_sold = Column(Integer, nullable=False)
    price_sold_without_vat= Column(Integer, nullable=False)
    sale = relationship('Sale', back_populates='items')
    product_option = relationship('ProductOption', back_populates='sale_items')



Index('idx_productoption_barcode',ProductOption.barcode_id)
Index('idx_productoption_product',ProductOption.product_PO_id)
Index('idx_product_category',Product.category_P_id)
Index('idx_sale_date',Sale.sale_date)
Index('idx_saleitem_sale',SaleItem.sale_SI_id)
Index('idx_product_brand', Product.brand_name)



Base.metadata.create_all(engine) #I need it to actually create the tables in ny database based on python models



def init_db():
    session = Session()
    try:
        categories = ['Smartphones','Laptops','Tablets','Smartwatches', 'Accessories']
        for cat_name in categories:
            session.add(ProductCategory(category_name = cat_name))
        session.commit()
        suppliers = [
            Supplier(supplier_name='TechGlobal Inc.', phone_number='+1-555-0123',
                    address='123 Tech Street, Silicon Valley, CA'),
            Supplier(supplier_name='Global Electronics', phone_number='+1-555-0124',
                    address='456 Electronics Ave, New York, NY'),
            Supplier(supplier_name='Digital Solutions',phone_number='+1-555-0125',
                    address='789 Digital Road, Seattle, WA'),
            Supplier(supplier_name='Smart Devices Co.',phone_number='+1-555-0126',
                    address='321 Smart Blvd, Austin, TX'),
            Supplier(supplier_name='Future Tech Ltd.',  phone_number='+1-555-0127',
                    address='654 Future Lane, Boston, MA')
        ]
        session.add_all(suppliers)
        session.commit()



        promo_code = PromoCode(
            code_id = 'WELCOME10',
            discount_percentage=10,
            valid_from=datetime(2024, 1,1).date(),
            valid_to=datetime(2024,12,31).date()
        )
        session.add(promo_code)
        session.commit()



        products_data = [
            ('iPhone 15 Pro',1, 'Apple', 'APP15P-256', 50, 80000, 99900),
            ('iPhone 15', 1, 'Apple', 'APP15-128',75, 60000, 79900),
            ('MacBook Pro 16', 2, 'Apple', 'APP-MBP16', 30,150000, 199900),
            ('iPad Pro 12.9',3, 'Apple', 'APP-IPAD12', 40, 80000, 99900),
            ('Apple Watch Series 9', 4, 'Apple', 'APP-WATCH9', 60, 30000, 39900),
            ('Galaxy S24 Ultra',1, 'Samsung','SAM-S24U', 45, 70000, 89900),
            ('Galaxy Book 4', 2, 'Samsung', 'SAM-BOOK4', 35, 120000,149900),
            ('Galaxy Tab S9',3, 'Samsung', 'SAM-TABS9', 50, 60000, 79900),
            ('Galaxy Watch 6', 4, 'Samsung', 'SAM-WATCH6', 55, 25000,29900),
            ('Galaxy Buds Pro', 5,'Samsung', 'SAM-BUDSP',80, 15000, 19900),
            ('Xperia 1 V', 1, 'Sony', 'SON-XP1V', 40, 75000, 94900),
            ('VAIO SX14', 2, 'Sony', 'SON-VAIO14', 25, 130000,169900),
            ('Xperia Tablet Z4', 3, 'Sony', 'SON-TABZ4', 30, 70000, 89900),
            ('WH-1000XM5',5, 'Sony','SON-WH1000', 65, 20000, 29900),
            ('WF-1000XM5', 5, 'Sony', 'SON-WF1000', 70, 15000, 19900),
            ('XPS 15', 2, 'Dell', 'DEL-XPS15',40, 140000, 179900),
            ('Alienware m18', 2, 'Dell', 'DEL-ALIEN18', 25,180000,229900),
            ('Latitude 7440', 2, 'Dell','DEL-LAT7440', 35, 110000, 139900),
            ('Dell XPS 13',2, 'Dell', 'DEL-XPS13', 45, 90000,119900),
            ('Dell Inspiron 16', 2, 'Dell', 'DEL-INS16', 50, 70000, 89900),
            ('ThinkPad X1 Carbon', 2, 'Lenovo','LEN-X1C', 40, 120000,149900),
            ('Yoga 9i', 2, 'Lenovo', 'LEN-YOGA9', 35, 100000, 129900),
            ('Tab P12 Pro',3, 'Lenovo', 'LEN-TABP12', 45, 65000, 84900),
            ('ThinkPad X13', 2, 'Lenovo', 'LEN-X13', 55, 85000, 109900),
            ('IdeaPad 5', 2, 'Lenovo', 'LEN-IDEA5', 60, 60000,79900)
        ]



        color_attr=AttributeName(attribute_name='Color')
        session.add(color_attr)
        session.commit()
        colors = ['Black','White','Silver','Blue','Red','Green']
        color_values ={}
        for color in colors:
            color_value = AttributeValue(attribute_value = color)
            session.add(color_value)
            session.commit()
            color_values[color] = color_value.attribute_value_id
        for product in products_data:
            new_product = Product(
                model=product[0],
                category_P_id=product[1],
                brand_name = product[2]
            )
            session.add(new_product)
            session.commit()
            product_option=ProductOption(
                barcode_id=product[3],
                product_PO_id=new_product.product_id,
                quantity=product[4],
                wholesale_price=product[5],
                sale_price=product[6]
            )
            session.add(product_option)
            session.commit()
            random_color= random.choice(colors)
            product_attr = ProductAttribute(
                barcode_PA_id=product_option.barcode_id,
                attribute_name_id=color_attr.attribute_name_id,
                attribute_value_id=color_values[random_color]
            )
            session.add(product_attr)
            price_history = PriceHistory(
                barcode_PH_id=product_option.barcode_id,
                old_price=product[5],
                new_price=product[6],
                change_date=datetime.now()
            )
            session.add(price_history)
            product_supplier=ProductSupplier(
                product_PS_id=new_product.product_id,
                supplier_PS_id=random.randint(1,5)
            )
            session.add(product_supplier)
        session.commit()



        sale_items_data = [
            ('APP15P-256', 99900),
            ('APP15-128', 79900),
            ('SAM-S24U', 89900),
            ('SON-XP1V', 94900),
            ('APP-MBP16', 199900),
            ('DEL-XPS15', 179900),
            ('LEN-X1C', 149900),
            ('SAM-BOOK4',149900),
            ('APP-IPAD12',99900),
            ('SAM-TABS9', 79900),
            ('LEN-TABP12', 84900),
            ('APP-WATCH9',39900),
            ('SAM-WATCH6', 29900),
            ('SAM-BUDSP', 19900),
            ('SON-WH1000', 29900),
            ('SON-WF1000', 19900)
        ]



        current_date = datetime.now()
        start_date = current_date - timedelta(days = 365)
        for _ in range(1500):
            random_days = random.randint(0,365)
            sale_date = start_date + timedelta(days=random_days)
            sale_source = random.choice(['Online','Store'])
            promo_code = random.choice(['WELCOME10', None])
            sale_tax_rate = 20
            sale=Sale(
                sale_date=sale_date,
                source_name=sale_source,
                code_S_id=promo_code,
                tax_rate=sale_tax_rate
            )
            session.add(sale)
            session.commit()
            items_in_sale = random.sample(sale_items_data, random.randint(1, 10))
            for item in items_in_sale:
                sale_item= SaleItem(
                    sale_SI_id=sale.sale_id,
                    barcode_SI_id=item[0],
                    quantity_sold=random.randint(1, 10),
                    price_sold_without_vat=item[1]
                )
                session.add(sale_item)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()



if __name__ == '__main__':
    init_db()
