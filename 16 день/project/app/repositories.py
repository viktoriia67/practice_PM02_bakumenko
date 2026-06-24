import datetime

from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

import httpx



from app.models import Order, OrderItem, OrderStatus

from app.exceptions import (

    EntityNotFoundException,

    InvalidOrderStatusException,

    DeliveryCalculationException,

    InvalidOrderDataException

)



class OrderRepository:

    """Репозиторий для изоляции работы с БД и бизнес-логики управления заказами."""

    

    def __init__(self, session: Session):

        self.session = session

        self.delivery_api_url = "http://localhost:8000/api/delivery/calculate"



    def _calculate_items_total(self, items_data: List[Dict[str, Any]]) -> float:

        """Вспомогательный метод валидации и подсчета стоимости товаров."""

        total = 0.0

        for item in items_data:

            quantity = item.get('quantity')

            price = item.get('price')

            if not isinstance(quantity, int) or quantity <= 0:

                raise InvalidOrderDataException("Количество должно быть целым числом больше нуля.")

            if not isinstance(price, (int, float)) or price <= 0:

                raise InvalidOrderDataException("Цена товара должна быть положительным числом.")

            total += quantity * price

        return total



    def calculate_delivery_cost(self, address: str, total_items_amount: float) -> float:

        """Интеграционный метод. Делает HTTP-запрос к сторонней системе расчета доставки."""

        try:

            response = httpx.post(

                self.delivery_api_url,

                json={"address": address, "order_value": total_items_amount},

                timeout=5

            )

            response.raise_for_status()  # Генерирует HTTPStatusError при ошибках 4xx/5xx

            data = response.json()

            if "cost" not in data or not isinstance(data["cost"], (int, float)):

                raise DeliveryCalculationException("Некорректный формат ответа от API доставки.")

            if data["cost"] < 0:

                raise DeliveryCalculationException("Стоимость доставки не может быть отрицательной.")

            return float(data["cost"])

        except httpx.RequestError as e:

            raise DeliveryCalculationException(f"Сетевой сбой при обращении к API доставки: {e}")

        except httpx.HTTPStatusError as e:

            raise DeliveryCalculationException(f"Ошибка API доставки: статус {e.response.status_code}")



    def create_order_data_dict(self, order_data: Dict[str, Any]) -> Order:

        """

        Создание заказа. Использует принцип транзакционности: 

        если API доставки падает, изменения откатываются (rollback).

        """

        try:

            customer_name = order_data.get('customer_name')

            delivery_address = order_data.get('delivery_address')

            items_data = order_data.get('items')



            if not customer_name or not delivery_address or not items_data:

                raise InvalidOrderDataException("Отсутствуют обязательные данные заказа.")



            # 1. Считаем стоимость товаров с валидацией данных

            total_items_amount = self._calculate_items_total(items_data)

            

            # 2. Вычисляем доставку через внешний API

            delivery_cost = self.calculate_delivery_cost(delivery_address, total_items_amount)



            # 3. Сохраняем заказ в БД

            new_order = Order(

                customer_name=customer_name,

                delivery_address=delivery_address,

                total_items_amount=total_items_amount,

                delivery_cost=delivery_cost,

                total_amount=total_items_amount + delivery_cost,

                status=OrderStatus.PENDING

            )

            self.session.add(new_order)

            self.session.flush()



            # Добавляем позиции заказа

            for item_data in items_data:

                item = OrderItem(

                    order_id=new_order.id,

                    product_name=item_data['product_name'],

                    quantity=item_data['quantity'],

                    price=item_data['price']

                )

                self.session.add(item)

                

            self.session.commit()

            self.session.refresh(new_order)

            return new_order

            

        except Exception as e:

            self.session.rollback()  # Гарантия атомарности операции

            raise e



    def find_by_id(self, order_id: int) -> Optional[Order]:

        """Поиск заказа по ID."""

        return self.session.query(Order).filter(Order.id == order_id).first()



    def find_all_by_status(self, status: str) -> List[Order]:

        """Поиск списка заказов по строковому представлению статуса."""

        if not OrderStatus.has_value(status):

            raise InvalidOrderStatusException(f"Статус '{status}' не валиден.")

        return self.session.query(Order).filter(Order.status == OrderStatus[status]).all()



    def find_orders_by_date_range(self, start_date: datetime.datetime, end_date: datetime.datetime) -> List[Order]:

        """Поиск заказов по временному интервалу."""

        return self.session.query(Order).filter(

            Order.created_at >= start_date,

            Order.created_at <= end_date

        ).all()



    def get_order_total_amount(self, order_id: int) -> float:

        """Получение полной стоимости заказа."""

        order = self.find_by_id(order_id)

        if not order:

            raise EntityNotFoundException(f"Заказ с ID {order_id} не найден.")

        return order.total_amount



    def update_status(self, order_id: int, new_status: str) -> Order:

        """Обновление статуса заказа с валидацией."""

        order = self.find_by_id(order_id)

        if not order:

            raise EntityNotFoundException(f"Заказ с ID {order_id} не найден.")

        if not OrderStatus.has_value(new_status):

            raise InvalidOrderStatusException(f"Недопустимый статус '{new_status}'.")

        

        order.status = OrderStatus[new_status]

        self.session.commit()

        self.session.refresh(order)

        return order



    def delete_order(self, order_id: int) -> None:

        """Удаление заказа. Позиции удаляются каскадно на уровне связей моделей."""

        order = self.find_by_id(order_id)

        if not order:

            raise EntityNotFoundException(f"Заказ с ID {order_id} не найден.")

        self.session.delete(order)

        self.session.commit()

