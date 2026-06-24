import datetime

import pytest

import httpx

from sqlalchemy.orm import Session



from app.models import Order, OrderItem, OrderStatus

from app.repositories import OrderRepository

from app.exceptions import (

    EntityNotFoundException,

    InvalidOrderStatusException,

    DeliveryCalculationException,

    InvalidOrderDataException

)



@pytest.fixture

def sample_order_data():

    return {

        "customer_name": "Иван Иванов",

        "delivery_address": "Ул. Пушкина, 10",

        "items": [

            {"product_name": "Клавиатура", "quantity": 1, "price": 100.0},

            {"product_name": "Кабель", "quantity": 2, "price": 10.0},

        ]

    }



@pytest.fixture

def mock_delivery_success(respx_mock):

    respx_mock.post("http://localhost:8000/api/delivery/calculate").mock(

        return_value=httpx.Response(200, json={"cost": 50.0})

    )



# --- Блок тестов создания и транзакционности ---



def test_create_order_success(order_repository, sample_order_data, db_session, mock_delivery_success):

    # Arrange (подготовка данных выполнена фикстурами)

    # Act

    order = order_repository.create_order_data_dict(sample_order_data)



    # Assert

    assert order.id is not None

    assert order.total_items_amount == 120.0  # 100 + 2*10

    assert order.delivery_cost == 50.0

    assert order.total_amount == 170.0

    assert len(order.items) == 2



def test_create_order_api_delivery_500_error_rollback(order_repository, sample_order_data, db_session, respx_mock):

    # Arrange: эмулируем ошибку 500 на сервере доставки

    respx_mock.post("http://localhost:8000/api/delivery/calculate").mock(

        return_value=httpx.Response(500, text="Internal Server Error")

    )



    # Act & Assert: ожидаем падение с исключением и проверяем откат транзакции (БД пуста)

    with pytest.raises(DeliveryCalculationException, match="Ошибка API доставки"):

        order_repository.create_order_data_dict(sample_order_data)

        

    assert db_session.query(Order).count() == 0

    assert db_session.query(OrderItem).count() == 0



@pytest.mark.parametrize("quantity, price, expected_err", [

    (-5, 100.0, "Количество должно быть целым числом"),

    (2, -10.0, "Цена товара должна быть положительным числом"),

])

def test_create_order_invalid_data_validation(order_repository, sample_order_data, quantity, price, expected_err, mock_delivery_success):

    # Arrange

    invalid_data = sample_order_data.copy()

    invalid_data["items"] = [{"product_name": "Тест", "quantity": quantity, "price": price}]

    

    # Act & Assert

    with pytest.raises(InvalidOrderDataException, match=expected_err):

        order_repository.create_order_data_dict(invalid_data)



# --- Блок тестов удаления и поиска ---



def test_cascade_delete_order(order_repository, sample_order_data, db_session, mock_delivery_success):

    # Arrange

    order = order_repository.create_order_data_dict(sample_order_data)

    order_id = order.id

    item_ids = [item.id for item in order.items]



    # Act: Удаляем заказ

    order_repository.delete_order(order_id)



    # Assert: Проверяем каскадное удаление заказа и всех его позиций

    assert order_repository.find_by_id(order_id) is None

    for item_id in item_ids:

        assert db_session.get(OrderItem, item_id) is None



def test_find_orders_by_date_range(order_repository, sample_order_data, db_session, mock_delivery_success):

    # Arrange

    o1 = order_repository.create_order_data_dict(sample_order_data)

    o1.created_at = datetime.datetime(2026, 6, 1)

    

    o2 = order_repository.create_order_data_dict(sample_order_data)

    o2.created_at = datetime.datetime(2026, 6, 15)

    db_session.commit()



    # Act

    found = order_repository.find_orders_by_date_range(

        datetime.datetime(2026, 6, 10), 

        datetime.datetime(2026, 6, 20)

    )



    # Assert

    assert len(found) == 1

    assert found[0].id == o2.id



# --- Блок контрактных тестов внешнего API ---



def test_calculate_delivery_cost_network_error(order_repository, respx_mock):

    # Arrange: эмулируем падение физического соединения сети

    respx_mock.post("http://localhost:8000/api/delivery/calculate").mock(

        side_effect=httpx.ConnectError("Network is down")

    )



    # Act & Assert

    with pytest.raises(DeliveryCalculationException, match="Сетевой сбой"):

        order_repository.calculate_delivery_cost("Адрес", 100.0)

