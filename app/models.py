Let's open database.py.import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)

    documents = relationship("Document", back_populates="owner")
    approvals = relationship("Approval", back_populates="approver")

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"


class DocumentStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="documents")

    approvals = relationship("Approval", back_populates="document", cascade="all, delete-orphan")

    @validates("status")
    def validate_status(self, key, value):
        if not isinstance(value, DocumentStatus):
            raise ValueError("Invalid status for document")
        return value

    def __repr__(self):
        return f"<Document id={self.id} title={self.title} status={self.status.value}>"


class ApprovalDecision(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    decision = Column(Enum(ApprovalDecision), nullable=False)
    comment = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="approvals")
    approver = relationship("User", back_populates="approvals")

    @validates("decision")
    def validate_decision(self, key, value):
        if not isinstance(value, ApprovalDecision):
            raise ValueError("Invalid decision for approval")
        return value

    def __repr__(self):
        return f"<Approval id={self.id} document_id={self.document_id} approver_id={self.approver_id} decision={self.decision.value}>"