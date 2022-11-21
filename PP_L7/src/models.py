from sqlalchemy.orm import declarative_base, sessionmaker, relationship, backref
from sqlalchemy import *

Base = declarative_base()


class FamilyBudgets(Base):
    __tablename__ = 'family_budgets'
    id = Column(Integer,
                Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
                primary_key=True, nullable=False)
    money_amount = Column(BigInteger, nullable=False, default=0)
    familyBudgetUsers_child = relationship("FamilyBudgetsUsers", cascade="all,delete",
                                           backref="familyBudgetUsers_parent_familyBudget")


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer,
                Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
                primary_key=True, nullable=False)
    surname = Column(String(40), nullable=False)
    name = Column(String(40), nullable=False)
    username = Column(String(40), nullable=False, unique=True)
    password = Column(String(256), nullable=False)
    personalBudget_child = relationship("PersonalBudgets", cascade="all,delete", backref="personalBudget_parent_user")
    familyBudgetUsers_child = relationship("FamilyBudgetsUsers", cascade="all,delete",
                                           backref="familyBudgetUsers_parent_user")


class PersonalBudgets(Base):
    __tablename__ = "personal_budgets"
    id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    money_amount = Column(BigInteger, nullable=False, default=0)


class FamilyBudgetsUsers(Base):
    __tablename__ = 'family_budgets_users'
    id = Column(Integer,
                Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
                primary_key=True, nullable=False)
    family_budget_id = Column(Integer, ForeignKey('family_budgets.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)


class Operation(Base):
    __tablename__ = 'operations'
    id = Column(Integer,
                Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
                primary_key=True, nullable=False)
    sender_id = Column(Integer, nullable=False)
    receiver_id = Column(Integer, nullable=False)
    sender_type = Column(String(40), nullable=False)
    receiver_type = Column(String(40), nullable=False)
    money_amount = Column(BigInteger, nullable=False)
    date = Column(DateTime, nullable=False)
