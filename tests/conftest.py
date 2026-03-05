import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.database import Base, get_db
from app.models import User, Request as ApprovalRequest

TEST_DATABASE_URL = "sqlite:///:memory:"


def _override_get_db() -> Session:
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    try:
        db = testing_session_local()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    event.listen(engine, "connect", lambda conn, rec: conn.execute("PRAGMA foreign_keys=ON"))
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def seed_users(db_session):
    users = [
        User(name="Alice", email="alice@example.com"),
        User(name="Bob", email="bob@example.com"),
    ]
    db_session.add_all(users)
    db_session.commit()
    return users


@pytest.fixture(scope="function")
def seed_requests(db_session, seed_users):
    requests = [
        ApprovalRequest(title="Approve Budget", description="Budget approval needed", user_id=seed_users[0].id),
        ApprovalRequest(title="New Hire", description="Hire request for dev", user_id=seed_users[1].id),
    ]
    db_session.add_all(requests)
    db_session.commit()
    return requests


@pytest.fixture(scope="function")
def cleanup(db_engine):
    yield
    connection = db_engine.connect()
    trans = connection.begin()
    for table in reversed(Base.metadata.sorted_tables):
        connection.execute(table.delete())
    trans.commit()
    connection.close()