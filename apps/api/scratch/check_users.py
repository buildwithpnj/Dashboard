import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def check_db():
    engine = create_engine("postgresql+psycopg2://personal_os:personal_os_dev@localhost:5432/personal_os")
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as session:
        rows = session.execute(text("SELECT id, email, role FROM users")).fetchall()
        print("=== DATABASE USER ROWS ===")
        for r in rows:
            print(f"ID: {r[0]}, Email: {r[1]}, Role: {r[2]}")
        print("==========================")

if __name__ == "__main__":
    check_db()
