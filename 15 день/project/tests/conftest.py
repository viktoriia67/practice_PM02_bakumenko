import pytest

import logging

from app.services import BankApiClient



@pytest.fixture

def mock_bank_client(mocker):

    """Фикстура для создания мок-объекта банковского клиента."""

    return mocker.Mock(spec=BankApiClient)



@pytest.fixture

def mock_logger(mocker):

    """Фикстура для создания мок-объекта логгера."""

    return mocker.Mock(spec=logging.Logger)
