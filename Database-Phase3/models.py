from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Define all models (tables)
class ProductCategory(Base):
    __tablename__ = 'ProductCategory'
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String, nullable=False)

class Product(Base):
    __tablename__ = 'Product'
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    model = Column(String, nullable=False)
    category_P_id = Column(Integer, ForeignKey('ProductCategory.category_id'))
    brand_name = Column(String)

class ProductOption(Base):
    __tablename__ = 'ProductOption'
    barcode_id = Column(String, primary_key=True)
    product_PO_id = Column(Integer, ForeignKey('Product.product_id'))
    quantity = Column(Integer, nullable=False)
    wholesale_price = Column(Integer, nullable=False)
    sale_price = Column(Integer, nullable=False)

class AttributeName(Base):
    __tablename__ = 'AttributeName'
    attribute_name_id = Column(Integer, primary_key=True, autoincrement=True)
    attribute_name = Column(String, nullable=False, unique=True)

class AttributeValue(Base):
    __tablename__ = 'AttributeValue'
    attribute_value_id = Column(Integer, primary_key=True, autoincrement=True)
    attribute_value = Column(String, nullable=False, unique=True)

class ProductAttribute(Base):
    __tablename__ = 'ProductAttribute'
    barcode_PA_id = Column(String, ForeignKey('ProductOption.barcode_id'), primary_key=True)
    attribute_name_id = Column(Integer, ForeignKey('AttributeName.attribute_name_id'), primary_key=True)
    attribute_value_id = Column(Integer, ForeignKey('AttributeValue.attribute_value_id'), primary_key=True)

class PriceHistory(Base):
    __tablename__ = 'PriceHistory'
    price_id = Column(Integer, primary_key=True, autoincrement=True)
    barcode_PH_id = Column(String, ForeignKey('ProductOption.barcode_id'))
    old_price = Column(Integer, nullable=False)
    new_price = Column(Integer, nullable=False)
    change_date = Column(DateTime, nullable=False)

class Supplier(Base):
    __tablename__ = 'Supplier'
    supplier_id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_name = Column(String, nullable=False)
    phone_number = Column(String)
    address = Column(String)

class ProductSupplier(Base):
    __tablename__ = 'ProductSupplier'
    product_PS_id = Column(Integer, ForeignKey('Product.product_id'), primary_key=True)
    supplier_PS_id = Column(Integer, ForeignKey('Supplier.supplier_id'), primary_key=True)

class PromoCode(Base):
    __tablename__ = 'PromoCode'
    code_id = Column(String, primary_key=True)
    discount_percentage = Column(Integer, nullable=False)
    valid_from = Column(String, nullable=False)  # Using String for simplicity
    valid_to = Column(String, nullable=False)

class Sale(Base):
    __tablename__ = 'Sale'
    sale_id = Column(Integer, primary_key=True, autoincrement=True)
    sale_date = Column(DateTime, nullable=False)
    source_name = Column(String)
    code_S_id = Column(String, ForeignKey('PromoCode.code_id'))
    tax_rate = Column(Integer)

class SaleItem(Base):
    __tablename__ = 'SaleItem'
    sale_item_id = Column(Integer, primary_key=True, autoincrement=True)
    sale_SI_id = Column(Integer, ForeignKey('Sale.sale_id'))
    barcode_SI_id = Column(String, ForeignKey('ProductOption.barcode_id'), nullable=False)
    quantity_sold = Column(Integer, nullable=False)
    price_sold_without_vat = Column(Integer, nullable=False)

# Create indexes
Index('idx_productoption_barcode', ProductOption.barcode_id)
Index('idx_productoption_product', ProductOption.product_PO_id)
Index('idx_product_category', Product.category_P_id)
Index('idx_sale_date', Sale.sale_date)
Index('idx_saleitem_sale', SaleItem.sale_SI_id)
Index('idx_product_brand', Product.brand_name)
