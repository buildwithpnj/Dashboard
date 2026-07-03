import asyncio
from datetime import datetime, timedelta

from argon2 import PasswordHasher
from sqlalchemy import select

from app.database import async_session_factory
from app.models.books import Book
from app.models.finance import Account, Category, Transaction
from app.models.user import User

ph = PasswordHasher()


async def seed_data():
    async with async_session_factory() as session:
        # Check if user already exists
        result = await session.execute(select(User).where(User.email == "test@example.com"))
        user = result.scalar_one_or_none()

        if not user:
            print("Creating test user: test@example.com / password123")
            user = User(
                email="test@example.com",
                password_hash=ph.hash("password123"),
            )
            session.add(user)
            await session.flush()
        else:
            print("Test user already exists.")

        # Seed categories if none exist for user
        cat_result = await session.execute(
            select(Category).where(Category.user_id == user.id).limit(1)
        )
        if not cat_result.scalar_one_or_none():
            print("Creating default categories...")
            categories = [
                Category(name="Salary", kind="income", user_id=user.id),
                Category(name="Freelance", kind="income", user_id=user.id),
                Category(name="Groceries", kind="expense", user_id=user.id),
                Category(name="Rent", kind="expense", user_id=user.id),
                Category(name="Utilities", kind="expense", user_id=user.id),
                Category(name="Dining Out", kind="expense", user_id=user.id),
                Category(name="Entertainment", kind="expense", user_id=user.id),
            ]
            session.add_all(categories)
            await session.flush()

            # Cache categories by name
            cat_map = {c.name: c for c in categories}
        else:
            print("Categories already exist.")
            cat_res = await session.execute(select(Category).where(Category.user_id == user.id))
            cat_map = {c.name: c for c in cat_res.scalars().all()}

        # Seed accounts if none exist
        acc_result = await session.execute(
            select(Account).where(Account.user_id == user.id).limit(1)
        )
        if not acc_result.scalar_one_or_none():
            print("Creating default accounts...")
            accounts = [
                Account(
                    user_id=user.id,
                    name="Main Checking Account",
                    type="bank",
                    currency="INR",
                    opening_balance=50000.00,
                ),
                Account(
                    user_id=user.id,
                    name="Cash Wallet",
                    type="cash",
                    currency="INR",
                    opening_balance=2500.00,
                ),
                Account(
                    user_id=user.id,
                    name="Credit Card",
                    type="card",
                    currency="INR",
                    opening_balance=0.00,
                ),
                Account(
                    user_id=user.id,
                    name="Mutual Funds Portfolio",
                    type="investment",
                    currency="INR",
                    opening_balance=120000.00,
                ),
            ]
            session.add_all(accounts)
            await session.flush()

            # Seed transactions
            print("Creating default transactions...")
            transactions = [
                # Checking account income/expense
                Transaction(
                    account_id=accounts[0].id,
                    amount=85000.00,
                    category_id=cat_map.get("Salary").id if "Salary" in cat_map else None,
                    merchant="Company Inc",
                    note="Monthly Salary Credit",
                    occurred_at=datetime.now() - timedelta(days=15),
                    source="manual",
                ),
                Transaction(
                    account_id=accounts[0].id,
                    amount=-18000.00,
                    category_id=cat_map.get("Rent").id if "Rent" in cat_map else None,
                    merchant="Landlord",
                    note="Apartment Rent",
                    occurred_at=datetime.now() - timedelta(days=14),
                    source="manual",
                ),
                Transaction(
                    account_id=accounts[0].id,
                    amount=-4200.00,
                    category_id=cat_map.get("Utilities").id if "Utilities" in cat_map else None,
                    merchant="Power Grid",
                    note="Electricity Bill",
                    occurred_at=datetime.now() - timedelta(days=10),
                    source="manual",
                ),
                # Credit Card expenses
                Transaction(
                    account_id=accounts[2].id,
                    amount=-3500.00,
                    category_id=cat_map.get("Groceries").id if "Groceries" in cat_map else None,
                    merchant="Supermarket",
                    note="Weekly Groceries",
                    occurred_at=datetime.now() - timedelta(days=5),
                    source="manual",
                ),
                Transaction(
                    account_id=accounts[2].id,
                    amount=-1200.00,
                    category_id=cat_map.get("Dining Out").id if "Dining Out" in cat_map else None,
                    merchant="Pizzeria",
                    note="Dinner with friends",
                    occurred_at=datetime.now() - timedelta(days=2),
                    source="manual",
                ),
            ]
            session.add_all(transactions)
        else:
            print("Accounts already exist.")

        # Seed books if none exist
        book_result = await session.execute(select(Book).where(Book.user_id == user.id).limit(1))
        if not book_result.scalar_one_or_none():
            print("Creating default books...")
            books = [
                Book(
                    user_id=user.id,
                    title="Atomic Habits",
                    author="James Clear",
                    status="reading",
                    rating=None,
                    started_at=datetime.now() - timedelta(days=7),
                    cover_url="https://images-na.ssl-images-amazon.com/images/I/91bYsX41hL.jpg",
                ),
                Book(
                    user_id=user.id,
                    title="Deep Work",
                    author="Cal Newport",
                    status="finished",
                    rating=5,
                    started_at=datetime.now() - timedelta(days=20),
                    finished_at=datetime.now() - timedelta(days=10),
                    cover_url="https://images-na.ssl-images-amazon.com/images/I/41757vP4k4L.jpg",
                ),
                Book(
                    user_id=user.id,
                    title="Clean Code",
                    author="Robert C. Martin",
                    status="to-read",
                    rating=None,
                    cover_url="https://images-na.ssl-images-amazon.com/images/I/41xSh45g7tL.jpg",
                ),
            ]
            session.add_all(books)
        else:
            print("Books already exist.")

        await session.commit()
        print("Database successfully seeded!")


if __name__ == "__main__":
    asyncio.run(seed_data())
