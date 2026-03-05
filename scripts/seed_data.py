import os
import sys
import logging
from contextlib import contextmanager

from sqlalchemy.exc import SQLAlchemyError

from app.database import get_session_local
from app.models import User, Document, Approval
from app.utils import hash_password

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

@contextmanager
def session_scope():
    session = get_session_local()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def create_users(session):
    users_data = [
        {"username": "alice", "email": "alice@example.com", "password": "alice123"},
        {"username": "bob", "email": "bob@example.com", "password": "bob123"},
        {"username": "carol", "email": "carol@example.com", "password": "carol123"},
    ]
    users = []
    for data in users_data:
        user = User(
            username=data["username"],
            email=data["email"],
            hashed_password=hash_password(data["password"]),
        )
        session.add(user)
        users.append(user)
    return users

def create_documents(session, users):
    docs_data = [
        {"title": "Budget Proposal", "content": "Proposal for Q3 budget.", "owner_id": users[0].id},
        {"title": "Project Plan", "content": "Plan for new feature rollout.", "owner_id": users[1].id},
        {"title": "Marketing Strategy", "content": "Strategy for upcoming campaign.", "owner_id": users[2].id},
    ]
    documents = []
    for data in docs_data:
        doc = Document(
            title=data["title"],
            content=data["content"],
            owner_id=data["owner_id"],
        )
        session.add(doc)
        documents.append(doc)
    return documents

def create_approvals(session, users, documents):
    approvals_data = [
        {"document_id": documents[0].id, "approver_id": users[1].id, "status": "pending"},
        {"document_id": documents[0].id, "approver_id": users[2].id, "status": "pending"},
        {"document_id": documents[1].id, "approver_id": users[0].id, "status": "approved"},
    ]
    for data in approvals_data:
        approval = Approval(
            document_id=data["document_id"],
            approver_id=data["approver_id"],
            status=data["status"],
        )
        session.add(approval)

def main():
    if os.getenv("APP_ENV") == "production":
        logger.warning("Running seed script in production environment. Aborting.")
        sys.exit(1)
    try:
        with session_scope() as session:
            users = create_users(session)
            documents = create_documents(session, users)
            create_approvals(session, users, documents)
        logger.info("Database seeding completed successfully.")
    except SQLAlchemyError as e:
        logger.error(f"Database error during seeding: {e}")
        sys.exit(1)
    except Exception as exc:
        logger.exception(f"Unexpected error: {exc}")
        sys.exit(1)

if __name__ == "__main__":
    main()