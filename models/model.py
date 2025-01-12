from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import date
from decimal import Decimal

class Subscription(SQLModel, table=True):
    id: int = Field(primary_key=True)
    empresa: str
    site: Optional[str] = None
    data_assinatura: date
    valor: Decimal

    payments: list['Payment'] = Relationship(back_populates='subscription', cascade_delete=True)

class Payment(SQLModel, table=True):
    id: int = Field(primary_key=True)
    subscription_id: int = Field(foreign_key="subscription.id", ondelete='CASCADE')
    date: date
    subscription: Subscription = Relationship(back_populates='payments')
