from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError


# MODELS ----------------------------------------------

Base = declarative_base()

class Product(Base):
  __tablename__ = "products"
  id = Column(Integer, primary_key = True)
  name = Column(String)
  price = Column(Float)
  description = Column(Text)


class Stock(Base):
  __tablename__ = "stocks"
  id = Column(Integer, primary_key=True)
  product_id = Column(Integer, ForeignKey('products.id'))
  quantity = Column(Integer, default=0)
  
# CUSTOM EXCEPTIONS ----------------------------------

class ProductException(Exception):
    """Exception raised when a product is not found in the inventory."""

    def __init__(self, product_id, message="Product not found"):
        self.product_id = product_id
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} - ID: {self.product_id}"


# CRUD functionality ---------------------------------

def addProduct(session, name, price, description):
  try:
    existing_product = session.query(Product).filter(Product.name == name).first()
    if existing_product:
      print("Product with that name already exists")
    else:
      new_product = Product(name=name, price=price, description=description)
      session.add(new_product)
      session.flush()
      new_stock = Stock(new_product.id, 0)
      session.add(new_stock)

    session.commit()
        
  except SQLAlchemyError as e:
    session.rollback()
    print(f"Error in addProduct: {e}")


def addStock(session, product_id, quantity):
  try:
    stock = session.query(Stock).filter(Stock.product_id == product_id).first()
    if stock:
      stock.quantity += quantity
    else:
       raise ProductException(product_id=product_id)
    session.commit()   

  except SQLAlchemyError as e:
     session.rollback()
     print(f"Error in addStock: {e}")


def removeProductById(session, product_id):
  try:
    product = session.query(Product).filter(Product.id == product_id).first()
    if product:
      session.delete(product)
    else:
       raise ProductException(product_id=product_id)
  except SQLAlchemyError as e:
    session.rollback()
    print(f"Error in removeProductById: {e}")
      
  

def removeStock(session, product_id, quantity):
  try:
    stock = session.query(Stock).filter(Stock.product_id == product_id).first()
    if stock:
      stock.quantity = max(stock.quantity - quantity, 0)
    else:
       raise ProductException(product_id=product_id)
    session.commit()   

  except SQLAlchemyError as e:
    session.rollback()
    print(f"Error in addStock: {e}")




# ENGINE ---------------------------------------------
      
engine = create_engine('sqlite:///inventory.db')

def get_session():
  Base.metadata.create_all(engine)
  Session = sessionmaker(bind=engine)
  return Session()

def reset_database():
    # bad practice - just for testing
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


# TESTING --------------------------------------------
    
def test_models():
    session = get_session()

    # Creating a new product
    addProduct(session, "TV", 999, "Best TV", 10)

    # Querying the product
    product = session.query(Product).first()
    print(f"Product: {product.name}, Description: {product.description}, Price: {product.price}")

if __name__ == "__main__":
    test_models()
