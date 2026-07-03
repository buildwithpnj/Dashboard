import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.notes import Note
from app.models.user import User


async def main():
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    
    async with async_session() as session:
        # Check users
        users_result = await session.execute(select(User))
        users = users_result.scalars().all()
        print(f"Total Users: {len(users)}")
        for u in users:
            print(f" - User: {u.email} (ID: {u.id})")
            
        # Check notes
        notes_result = await session.execute(select(Note))
        notes = notes_result.scalars().all()
        print(f"Total Notes: {len(notes)}")
        for n in notes:
            print(f" - Note: {n.title} (ID: {n.id}, User ID: {n.user_id})")

if __name__ == "__main__":
    asyncio.run(main())
