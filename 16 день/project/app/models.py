import datetime

import enum

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum

from sqlalchemy.orm import declarative_base, relationship



Base = declarative_base()



class OrderStatus(enum.Enum):

    """Перечисление допустимых статусов заказа."""

    PENDING = "PENDING"

    PAID = "PAID"

    SHIPPED = "SHIPPED"

    CANCELLED = "CANCELLED"



    @classmethod

    def has_value(cls, value):

        return value in set(item.value for item in cls)



class Order(Base):

    """Модель таблицы заказов."""

    __tablename__ = 'orders'



    id = Column(Integer, primary_key=True, autoincrement=True)

    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    customer_name = Column(String, nullable=False)

    delivery_address = Column(String, nullable=False)

    total_amount = Column(Float, nullable=False)  # Итоговая сумма (позиции + доставка)

    total_items_amount = Column(Float, nullable=False)  # Сумма только по позициям

    delivery_cost = Column(Float, nullable=False, default=0.0)



    # Каскадное отношение: при удалении заказа удаляются и связанные позиции

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="joined")



class OrderItem(Base):

    """Модель таблицы позиций (товаров) в заказе."""

    __tablename__ = 'order_items'



    id = Column(Integer, primary_key=True, autoincrement=True)

    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)

    product_name = Column(String, nullable=False)

    quantity = Column(Integer, nullable=False)

    price = Column(Float, nullable=False)



    order = relationship("Order", back_populates="items")

