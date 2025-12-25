from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    
    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

class Token(Base):
    __tablename__ = "tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, nullable=False, unique=True, index=True) 
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_valid = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="tokens")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="orders")
    goods = relationship("Good", back_populates="order", cascade="all, delete-orphan")

class Good(Base):
    __tablename__ = "goods"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    count = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    
    order = relationship("Order", back_populates="goods")