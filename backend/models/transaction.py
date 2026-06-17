from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Establish relationship to transactions
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    date = Column(String)
    description = Column(String)
    category = Column(String)
    amount = Column(Float)
    source_file = Column(String)
    
    # ForeignKey relation to User
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Scoped relationship back to User
    user = relationship("User", back_populates="transactions")

    __table_args__ = (
        UniqueConstraint('date', 'description', 'amount', 'user_id', name='uix_date_desc_amount_user'),
    )