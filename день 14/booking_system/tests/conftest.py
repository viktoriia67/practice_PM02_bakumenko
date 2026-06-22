

import pytest

# Импортируем из локального файла с реализациями для тестов!
from tests.unit_of_work import InMemoryUnitOfWork

@pytest.fixture(autouse=True)
def uow():
    return InMemoryUnitOfWork()