import pytest

from app.services import PaymentService

from app.exceptions import PaymentFailedException



def test_payment_success_first_attempt(mock_bank_client, mock_logger):

    """Тест успешной оплаты с первой попытки."""

    # Arrange

    # Настраиваем мок клиента: первый вызов успешен (возвращает True)

    mock_bank_client.charge.return_value = True

    service = PaymentService(bank_client=mock_bank_client, logger=mock_logger)



    # Act

    result = service.process_payment(100.0)



    # Assert

    assert result is True

    mock_bank_client.charge.assert_called_once_with(100.0)

    

    # Проверка побочного эффекта (логирование успешной операции)

    mock_logger.info.assert_called_once_with("Payment processed successfully")





def test_payment_success_after_retries(mock_bank_client, mock_logger):

    """Тест успешной оплаты со второй попытки после TimeoutError."""

    # Arrange

    # Имитируем ошибку при первом вызове и успех при втором

    mock_bank_client.charge.side_effect = [TimeoutError(), True]

    service = PaymentService(bank_client=mock_bank_client, logger=mock_logger)



    # Act

    result = service.process_payment(150.0)



    # Assert

    assert result is True

    assert mock_bank_client.charge.call_count == 2

    

    # Лог успешного завершения должен быть записан один раз

    mock_logger.info.assert_called_once_with("Payment processed successfully")





def test_payment_retry_exhausted(mock_bank_client, mock_logger):

    """Тест превышения лимита попыток при постоянном падении соединения."""

    # Arrange

    # Задаем стабильный выброс TimeoutError на все запросы

    mock_bank_client.charge.side_effect = TimeoutError()

    service = PaymentService(bank_client=mock_bank_client, logger=mock_logger)



    # Act & Assert

    with pytest.raises(PaymentFailedException) as exc_info:

        service.process_payment(200.0)



    assert str(exc_info.value) == "Payment failed after retries"

    

    # Проверяем, что было ровно 3 вызова (первая попытка + 2 повтора)

    assert mock_bank_client.charge.call_count == 3

    

    # Логирование успешного проведения НЕ должно выполняться

    mock_logger.info.assert_not_called()





def test_payment_invalid_amount(mock_bank_client, mock_logger):

    """Тест валидации суммы платежа (отрицательная сумма)."""

    # Arrange

    service = PaymentService(bank_client=mock_bank_client, logger=mock_logger)



    # Act & Assert

    with pytest.raises(ValueError) as exc_info:

        service.process_payment(-50.0)



    assert str(exc_info.value) == "Amount must be positive"

    

    # Клиент и логгер не должны вызываться

    mock_bank_client.charge.assert_not_called()

    mock_logger.info.assert_not_called()

