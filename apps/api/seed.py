"""
Synchronous database seeding — safe to call from any thread.

Uses a plain SQLAlchemy sync engine (psycopg2) so it never touches
FastAPI's asyncio event loop.
"""
import re
import uuid
from datetime import datetime, timedelta

from argon2 import PasswordHasher
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

ph = PasswordHasher()


def _sync_url(async_url: str) -> str:
    """Convert postgresql+asyncpg://... → postgresql+psycopg2://..."""
    return re.sub(r"^postgresql\+asyncpg://", "postgresql+psycopg2://", async_url)


def seed_sync():
    """
    Idempotent seed: creates default users & sample data if they don't exist.
    Safe to call from any thread — uses a sync engine that is created and
    destroyed entirely within this function.
    """
    sync_url = _sync_url(settings.database_url)
    engine = create_engine(sync_url, echo=False)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    with SessionLocal() as session:
        try:
            _seed_users(session)
            session.commit()
            print("Database successfully seeded for all users!")
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    engine.dispose()


def _seed_users(session: Session):
    # 1. test@example.com
    row = session.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": "test@example.com"},
    ).fetchone()
    if row is None:
        print("Creating test user: test@example.com / password123")
        uid_val = str(uuid.uuid4())
        session.execute(
            text("INSERT INTO users (id, email, password_hash, role) VALUES (:id, :email, :pw, :role)"),
            {"id": uid_val, "email": "test@example.com", "pw": ph.hash("password123"), "role": "approved_user"},
        )
        session.flush()
        row = session.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": "test@example.com"},
        ).fetchone()
        print("Test user created.")
    else:
        print("Test user already exists.")
    assert row is not None
    user_id = row[0]

    # 2. prakashjhadps@gmail.com
    row_pj = session.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": "prakashjhadps@gmail.com"},
    ).fetchone()
    if row_pj is None:
        print("Creating user: prakashjhadps@gmail.com / password123")
        uid_pj_val = str(uuid.uuid4())
        session.execute(
            text("INSERT INTO users (id, email, password_hash, role) VALUES (:id, :email, :pw, :role)"),
            {"id": uid_pj_val, "email": "prakashjhadps@gmail.com", "pw": ph.hash("password123"), "role": "approved_user"},
        )
        session.flush()
        row_pj = session.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": "prakashjhadps@gmail.com"},
        ).fetchone()
        print("prakashjhadps@gmail.com user created.")
    else:
        print("prakashjhadps@gmail.com user already exists.")
    assert row_pj is not None
    user_pj_id = row_pj[0]

    # Seed resources for both users
    for uid in [user_id, user_pj_id]:
        _seed_resources(session, uid)


def _seed_resources(session: Session, user_id: int):
    # Categories
    cat_count = session.execute(
        text("SELECT COUNT(*) FROM categories WHERE user_id = :uid"),
        {"uid": user_id},
    ).scalar()
    if cat_count == 0:
        print(f"Creating default categories for user {user_id}...")
        default_categories = [
            ("Salary", "income"),
            ("Freelance", "income"),
            ("Groceries", "expense"),
            ("Rent", "expense"),
            ("Utilities", "expense"),
            ("Dining Out", "expense"),
            ("Entertainment", "expense"),
        ]
        for name, kind in default_categories:
            cat_id = str(uuid.uuid4())
            session.execute(
                text("INSERT INTO categories (id, name, kind, user_id) VALUES (:id, :n, :k, :uid)"),
                {"id": cat_id, "n": name, "k": kind, "uid": user_id},
            )
        session.flush()
    else:
        print(f"Categories already exist for user {user_id}.")

    # Accounts
    acc_count = session.execute(
        text("SELECT COUNT(*) FROM accounts WHERE user_id = :uid"),
        {"uid": user_id},
    ).scalar()
    if acc_count == 0:
        print(f"Creating default accounts for user {user_id}...")
        accounts = [
            ("Main Checking Account", "bank", 50000.00),
            ("Cash Wallet", "cash", 2500.00),
            ("Credit Card", "card", 0.00),
            ("Mutual Funds Portfolio", "investment", 120000.00),
        ]
        for name, atype, balance in accounts:
            acc_id = str(uuid.uuid4())
            session.execute(
                text(
                    "INSERT INTO accounts (id, user_id, name, type, currency, opening_balance)"
                    " VALUES (:id, :uid, :name, :type, 'INR', :bal)"
                ),
                {"id": acc_id, "uid": user_id, "name": name, "type": atype, "bal": balance},
            )
        session.flush()

        # Get account ids for transactions
        acc_rows = session.execute(
            text("SELECT id, name FROM accounts WHERE user_id = :uid ORDER BY id"),
            {"uid": user_id},
        ).fetchall()
        acc_map = {row[1]: row[0] for row in acc_rows}

        # Get category ids
        cat_rows = session.execute(
            text("SELECT id, name FROM categories WHERE user_id = :uid"),
            {"uid": user_id},
        ).fetchall()
        cat_map = {row[1]: row[0] for row in cat_rows}

        now = datetime.now()
        txns = [
            (acc_map.get("Main Checking Account"), 85000.00, cat_map.get("Salary"), "Company Inc", "Monthly Salary Credit", now - timedelta(days=15)),
            (acc_map.get("Main Checking Account"), -18000.00, cat_map.get("Rent"), "Landlord", "Apartment Rent", now - timedelta(days=14)),
            (acc_map.get("Main Checking Account"), -4200.00, cat_map.get("Utilities"), "Power Grid", "Electricity Bill", now - timedelta(days=10)),
            (acc_map.get("Credit Card"), -3500.00, cat_map.get("Groceries"), "Supermarket", "Weekly Groceries", now - timedelta(days=5)),
            (acc_map.get("Credit Card"), -1200.00, cat_map.get("Dining Out"), "Pizzeria", "Dinner with friends", now - timedelta(days=2)),
        ]
        for txn_acc_id, amount, txn_cat_id, merchant, note, occurred_at in txns:
            if txn_acc_id:
                txn_id = str(uuid.uuid4())
                session.execute(
                    text(
                        "INSERT INTO transactions (id, account_id, amount, category_id, merchant, note, occurred_at, source)"
                        " VALUES (:id, :aid, :amt, :cid, :merchant, :note, :occ, 'manual')"
                    ),
                    {"id": txn_id, "aid": txn_acc_id, "amt": amount, "cid": txn_cat_id, "merchant": merchant, "note": note, "occ": occurred_at},
                )
        session.flush()
    else:
        print(f"Accounts/transactions already exist for user {user_id}.")

    # Books
    book_count = session.execute(
        text("SELECT COUNT(*) FROM books WHERE user_id = :uid"),
        {"uid": user_id},
    ).scalar()
    if book_count == 0:
        print(f"Creating default books for user {user_id}...")
        now = datetime.now()
        books = [
            ("Atomic Habits", "James Clear", "reading", None, now - timedelta(days=7), None,
             "https://images-na.ssl-images-amazon.com/images/I/91bYsX41hL.jpg"),
            ("Deep Work", "Cal Newport", "finished", 5, now - timedelta(days=20), now - timedelta(days=10),
             "https://images-na.ssl-images-amazon.com/images/I/41757vP4k4L.jpg"),
            ("Clean Code", "Robert C. Martin", "to-read", None, None, None,
             "https://images-na.ssl-images-amazon.com/images/I/41xSh45g7tL.jpg"),
        ]
        for title, author, status, rating, started_at, finished_at, cover_url in books:
            book_id = str(uuid.uuid4())
            session.execute(
                text(
                    "INSERT INTO books (id, user_id, title, author, status, rating, started_at, finished_at, cover_url)"
                    " VALUES (:id, :uid, :title, :author, :status, :rating, :started_at, :finished_at, :cover_url)"
                ),
                {
                    "id": book_id,
                    "uid": user_id,
                    "title": title,
                    "author": author,
                    "status": status,
                    "rating": rating,
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "cover_url": cover_url,
                },
            )
        session.flush()
    else:
        print(f"Books already exist for user {user_id}.")


# Allow running directly: python seed.py
if __name__ == "__main__":
    seed_sync()
