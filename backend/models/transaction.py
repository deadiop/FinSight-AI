from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


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

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    __table_args__ = (
        UniqueConstraint('date', 'description', 'amount', name='uix_date_desc_amount'),
    )