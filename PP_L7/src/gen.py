
import random
from faker import Faker
from src.db import session
from src.models import *

fake = Faker()


def create_user():
    users = session.query(User).all()
    pbudget = session.query(PBudget).all()
    fbudget = session.query(FBudget).all()

    for _ in range(10):
        user = User(
            email=fake.ascii_free_email(),
            password=fake.password(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
        )
        session.add(user)
    session.commit()


def create_pbudget():
    users = session.query(User).all()
    pbudget = session.query(PBudget).all()
    fbudget = session.query(FBudget).all()

    for l in users:
        pbudget = PBudget(
            balance=random.randint(0,10000),
            income=random.randint(0,10000),
            costs=random.randint(0,10000),
            user_id=l.id,
            )

        session.add(pbudget)
    session.commit()

def create_fbudget():
    users = session.query(User).all()
    pbudget = session.query(PBudget).all()
    fbudget = session.query(FBudget).all()

    for _ in range(10):
        fbudget = FBudget(
            balance=random.randint(0,10000),
            income=random.randint(0,10000),
            costs=random.randint(0,10000),
            date=fake.date(),
            )
        session.add(fbudget)
    session.commit()

def create_transactions():
    users = session.query(User).all()
    pbudget = session.query(PBudget).all()
    fbudget = session.query(FBudget).all()

    for l in pbudget:
        id_2=random.choice(fbudget)
        transfers = Transfer(
            amount=random.randint(0, 10000),
            addatetimedress=fake.date(),
            pbudget_id=l.pbudget_id,
            fbudget_id=id_2.fbudget_id,
            )
        session.add(transfers)
    session.commit()

def create_u_o_b():
    users = session.query(User).all()
    pbudget = session.query(PBudget).all()
    fbudget = session.query(FBudget).all()

    for l in users:
        id_2 = random.choice(fbudget)
        u_o_b = users_of_budget(
            user_id=l.id,
            fbudget_id=id_2.fbudget_id,
        )
        session.add(u_o_b)
    session.commit()


if __name__ == '__main__':
    create_user()
    create_pbudget()
    create_fbudget()
    create_transactions()
    create_u_o_b()