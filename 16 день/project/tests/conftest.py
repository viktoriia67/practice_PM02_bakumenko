import pytest

from sqlalchemy import create_engine

from sqlalchemy.orm import Session

from app.models import Base

from app.repositories import OrderRepository

import respx



@pytest.fixture(scope="function")

def db_session():

    """Создает чистую изолированную БД в оперативной памяти для каждого теста."""

    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    with Session(engine) as session:

        yield session

    Base.metadata.drop_all(engine)

    engine.dispose()



@pytest.fixture(scope="function")

def order_repository(db_session: Session) -> OrderRepository:

    """Инжектирует сессию БД в репозиторий."""

    return OrderRepository(db_session)



@pytest.fixture(scope="function")

def respx_mock():

    """Инициализирует мок-сервер для перехвата внешних HTTP-запросов."""

    with respx.mock as r:

        yield r
