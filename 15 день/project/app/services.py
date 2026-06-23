import logging

from app.exceptions import PaymentFailedException



class BankApiClient:

    """Внешний клиент платежного шлюза (интерфейс)."""

    def charge(self, amount: float) -> bool:

        # В реальной жизни здесь совершается сетевой запрос.

        # В тестах этот метод будет сымитирован.

        raise NotImplementedError("Реальные сетевые запросы запрещены в юнит-тестах.")



class PaymentService:

    """Сервис обработки платежей с механизмом повторных попыток."""

    def __init__(self, bank_client: BankApiClient, logger: logging.Logger = None):

        self.bank_client = bank_client

        self.logger = logger or logging.getLogger(__name__)



    def process_payment(self, amount: float) -> bool:

        """

        Проводит платеж. При возникновении TimeoutError делает до 3 попыток.

        Если все попытки завершились ошибкой, выбрасывает PaymentFailedException.

        """

        if amount <= 0:

            raise ValueError("Amount must be positive")



        max_retries = 3

        for attempt in range(max_retries):

            try:

                self.bank_client.charge(amount)

                # Если оплата прошла успешно

                if self.logger:

                    self.logger.info("Payment processed successfully")

                return True

            except TimeoutError:

                # Если попытки исчерпаны

                if attempt == max_retries - 1:

                    raise PaymentFailedException("Payment failed after retries")
