from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Table
from sqlalchemy.orm import relationship

from src.db import Base

# association_table = Table(
#     "association_table",
#     Base.metadata,
#     Column("left_id", ForeignKey("users.id")),
#     Column("right_id", ForeignKey("fbudget.fbudget_id")),
# )
class users_of_budget(Base):
    __tablename__ = 'u_o_b'
    id = Column(Integer, primary_key=True)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = relationship('User', back_populates='fbudget')
    fbudget_id = Column('fbudget_id', ForeignKey('fbudget.fbudget_id', ondelete='CASCADE'), nullable=False)
    fbudget = relationship('FBudget', back_populates='users')

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column('email', String(100), nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(120), nullable=True)
    last_name = Column(String(120), nullable=True)
    pbudget=relationship("PBudget", back_populates="user")
    fbudget = relationship("users_of_budget", back_populates="user")


class PBudget(Base):
    __tablename__ = 'pbudget'
    pbudget_id = Column(Integer, primary_key=True)
    balance = Column(Integer, nullable=False)
    income = Column(Integer, nullable=False)
    costs = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="pbudget")
    transfer = relationship('Transfer', back_populates='pbudget')

class FBudget(Base):
    __tablename__ = 'fbudget'
    fbudget_id = Column(Integer, primary_key=True)
    balance = Column(Integer, nullable=False)
    income = Column(Integer, nullable=False)
    costs = Column(Integer, nullable=False)
    date = Column(Date, nullable=True)
    users = relationship('users_of_budget', back_populates='fbudget')
    transfer = relationship('Transfer', back_populates='fbudget')

class Transfer(Base):
    __tablename__ = 'transfers'
    id = Column(Integer, primary_key=True)
    amount = Column(Integer, nullable=False)
    addatetimedress = Column(Date, nullable=False)
    pbudget_id = Column('pbudget_id', ForeignKey('pbudget.pbudget_id', ondelete='CASCADE'), nullable=False)
    pbudget = relationship('PBudget', back_populates='transfer')
    fbudget_id = Column('fbudget_id', ForeignKey('fbudget.fbudget_id', ondelete='CASCADE'), nullable=False)
    fbudget = relationship('FBudget', back_populates='transfer')