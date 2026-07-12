import asyncio
import io
import json
import logging
from datetime import datetime
from typing import List

from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.books import Book, Highlight
from app.models.finance import Account, Budget, Category, Transaction
from app.models.habits import Habit, HabitLog, JournalEntry
from app.models.notes import Note, NoteLink
from app.models.user import User

logger = logging.getLogger("gdrive_sync")

async def get_user_drive_service(user_id: str, db: AsyncSession):
    # Import locally to avoid circular dependency
    from app.routers.gdrive import get_drive_service
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise Exception("User not found")
    return await get_drive_service(user, db)

async def get_or_create_sync_folder(service) -> str:
    # Check if folder exists
    query = "name = 'WarBornOS' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get("files", [])
    
    if files:
        return files[0]["id"]
        
    # Create folder
    folder_metadata = {
        "name": "WarBornOS",
        "mimeType": "application/vnd.google-apps.folder"
    }
    folder = service.files().create(body=folder_metadata, fields="id").execute()
    return folder["id"]

async def upload_file_to_folder(service, folder_id: str, filename: str, content: str):
    # Check if file already exists in folder
    query = f"name = '{filename}' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get("files", [])
    
    file_metadata = {
        "name": filename,
        "parents": [folder_id]
    }
    
    fh = io.BytesIO(content.encode("utf-8"))
    media = MediaIoBaseUpload(fh, mimetype="application/json", resumable=True)
    
    if files:
        # Overwrite/Update existing file
        file_id = files[0]["id"]
        service.files().update(fileId=file_id, media_body=media).execute()
    else:
        # Create new file
        service.files().create(body=file_metadata, media_body=media, fields="id").execute()

async def download_file_from_folder(service, folder_id: str, filename: str) -> str | None:
    query = f"name = '{filename}' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get("files", [])
    
    if not files:
        return None
        
    file_id = files[0]["id"]
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        
    return fh.getvalue().decode("utf-8")


async def sync_section_to_gdrive(user_id: str, section: str, db: AsyncSession):
    # Fire and forget background task with its own database session
    asyncio.create_task(sync_section_background(user_id, section))

async def _sync_section_to_gdrive_impl(user_id: str, section: str, db: AsyncSession):
    try:
        service = await get_user_drive_service(user_id, db)
    except Exception as e:
        logger.info(f"GDrive not connected for user {user_id}. Skipping sync. Detail: {e}")
        return

    try:
        folder_id = await get_or_create_sync_folder(service)
    except Exception as e:
        logger.warning(f"GDrive sync failed for {section}: {e}")
        return

    data = {}
    
    if section == "notes":
        result = await db.execute(select(Note).where(Note.user_id == user_id))
        notes = result.scalars().all()
        note_ids = [n.id for n in notes]
        
        links: List[NoteLink] = []
        if note_ids:
            links_result = await db.execute(select(NoteLink).where(NoteLink.from_note_id.in_(note_ids)))
            links = list(links_result.scalars().all())
            
        data = {
            "notes": [
                {
                    "id": n.id,
                    "title": n.title,
                    "body_json": n.body_json,
                    "tags": n.tags,
                    "created_at": n.created_at.isoformat(),
                    "updated_at": n.updated_at.isoformat()
                } for n in notes
            ],
            "links": [
                {
                    "id": lnk.id,
                    "from_note_id": lnk.from_note_id,
                    "to_note_id": lnk.to_note_id
                } for lnk in links
            ]
        }
    elif section == "finance":
        accs_result = await db.execute(select(Account).where(Account.user_id == user_id))
        accs = accs_result.scalars().all()
        acc_ids = [a.id for a in accs]
        
        txs: List[Transaction] = []
        if acc_ids:
            txs_result = await db.execute(select(Transaction).where(Transaction.account_id.in_(acc_ids)))
            txs = list(txs_result.scalars().all())
            
        cats_result = await db.execute(select(Category).where(Category.user_id == user_id))
        cats = cats_result.scalars().all()
        
        buds_result = await db.execute(select(Budget).where(Budget.user_id == user_id))
        buds = buds_result.scalars().all()
        
        data = {
            "accounts": [
                {
                    "id": a.id,
                    "name": a.name,
                    "type": a.type,
                    "currency": a.currency,
                    "opening_balance": float(a.opening_balance),
                    "created_at": a.created_at.isoformat()
                } for a in accs
            ],
            "transactions": [
                {
                    "id": t.id,
                    "account_id": t.account_id,
                    "amount": float(t.amount),
                    "currency": t.currency,
                    "category_id": t.category_id,
                    "merchant": t.merchant,
                    "note": t.note,
                    "occurred_at": t.occurred_at.isoformat(),
                    "source": t.source,
                    "created_at": t.created_at.isoformat()
                } for t in txs
            ],
            "categories": [
                {
                    "id": c.id,
                    "name": c.name,
                    "parent_id": c.parent_id,
                    "kind": c.kind
                } for c in cats
            ],
            "budgets": [
                {
                    "id": b.id,
                    "category_id": b.category_id,
                    "amount_limit": float(b.amount_limit),
                    "period": b.period
                } for b in buds
            ]
        }
    elif section == "books":
        books_result = await db.execute(select(Book).where(Book.user_id == user_id))
        books = books_result.scalars().all()
        book_ids = [b.id for b in books]
        
        highlights: List[Highlight] = []
        if book_ids:
            hl_result = await db.execute(select(Highlight).where(Highlight.book_id.in_(book_ids)))
            highlights = list(hl_result.scalars().all())
            
        data = {
            "books": [
                {
                    "id": b.id,
                    "title": b.title,
                    "author": b.author,
                    "status": b.status,
                    "rating": b.rating,
                    "started_at": b.started_at.isoformat() if b.started_at else None,
                    "finished_at": b.finished_at.isoformat() if b.finished_at else None,
                    "cover_url": b.cover_url,
                    "created_at": b.created_at.isoformat(),
                    "updated_at": b.updated_at.isoformat()
                } for b in books
            ],
            "highlights": [
                {
                    "id": h.id,
                    "book_id": h.book_id,
                    "text": h.text,
                    "location": h.location,
                    "tags": h.tags,
                    "created_at": h.created_at.isoformat()
                } for h in highlights
            ]
        }
    elif section == "habits":
        habits_result = await db.execute(select(Habit).where(Habit.user_id == user_id))
        habits = habits_result.scalars().all()
        habit_ids = [h.id for h in habits]
        
        logs: List[HabitLog] = []
        if habit_ids:
            log_result = await db.execute(select(HabitLog).where(HabitLog.habit_id.in_(habit_ids)))
            logs = list(log_result.scalars().all())
            
        journal_result = await db.execute(select(JournalEntry).where(JournalEntry.user_id == user_id))
        journal = journal_result.scalars().all()
        
        data = {
            "habits": [
                {
                    "id": h.id,
                    "name": h.name,
                    "cadence": h.cadence,
                    "target": h.target,
                    "created_at": h.created_at.isoformat(),
                    "updated_at": h.updated_at.isoformat()
                } for h in habits
            ],
            "logs": [
                {
                    "id": log_item.id,
                    "habit_id": log_item.habit_id,
                    "date": log_item.date.isoformat(),
                    "value": float(log_item.value)
                } for log_item in logs
            ],
            "journal_entries": [
                {
                    "id": j.id,
                    "body_json": j.body_json,
                    "mood": j.mood,
                    "created_at": j.created_at.isoformat()
                } for j in journal
            ]
        }
        
    try:
        await upload_file_to_folder(service, folder_id, f"{section}.json", json.dumps(data, indent=2))
    except Exception as e:
        logger.warning(f"GDrive upload failed for {section}: {e}")

async def restore_section_from_gdrive(user_id: str, section: str, db: AsyncSession) -> bool:
    try:
        service = await get_user_drive_service(user_id, db)
    except Exception as e:
        logger.info(f"GDrive not connected for user {user_id}. Cannot restore. Detail: {e}")
        return False
        
    folder_id = await get_or_create_sync_folder(service)
    content = await download_file_from_folder(service, folder_id, f"{section}.json")
    
    if not content:
        return False
        
    data = json.loads(content)
    
    if section == "notes":
        # Delete existing
        result = await db.execute(select(Note).where(Note.user_id == user_id))
        notes = result.scalars().all()
        note_ids = [n.id for n in notes]
        if note_ids:
            await db.execute(delete(NoteLink).where(NoteLink.from_note_id.in_(note_ids)))
        await db.execute(delete(Note).where(Note.user_id == user_id))
        
        # Insert restored
        for n in data.get("notes", []):
            note = Note(
                id=n["id"],
                user_id=user_id,
                title=n["title"],
                body_json=n["body_json"],
                tags=n.get("tags"),
                created_at=datetime.fromisoformat(n["created_at"]),
                updated_at=datetime.fromisoformat(n["updated_at"])
            )
            db.add(note)
            
        for lnk in data.get("links", []):
            link = NoteLink(
                id=lnk["id"],
                from_note_id=lnk["from_note_id"],
                to_note_id=lnk["to_note_id"]
            )
            db.add(link)
            
    elif section == "finance":
        # Delete existing
        accs_result = await db.execute(select(Account).where(Account.user_id == user_id))
        accs = accs_result.scalars().all()
        acc_ids = [a.id for a in accs]
        
        if acc_ids:
            await db.execute(delete(Transaction).where(Transaction.account_id.in_(acc_ids)))
        await db.execute(delete(Budget).where(Budget.category_id.in_(
            select(Category.id).where(Category.user_id == user_id)
        )))
        await db.execute(delete(Category).where(Category.user_id == user_id))
        await db.execute(delete(Account).where(Account.user_id == user_id))
        
        # Insert categories first
        for c in data.get("categories", []):
            cat = Category(
                id=c["id"],
                user_id=user_id,
                name=c["name"],
                parent_id=c.get("parent_id"),
                kind=c["kind"]
            )
            db.add(cat)
            
        await db.flush() # ensure category IDs are registered
        
        # Insert accounts
        for a in data.get("accounts", []):
            acc = Account(
                id=a["id"],
                user_id=user_id,
                name=a["name"],
                type=a["type"],
                currency=a["currency"],
                opening_balance=a["opening_balance"],
                created_at=datetime.fromisoformat(a["created_at"])
            )
            db.add(acc)
            
        # Insert transactions
        for t in data.get("transactions", []):
            tx = Transaction(
                id=t["id"],
                account_id=t["account_id"],
                amount=t["amount"],
                currency=t["currency"],
                category_id=t.get("category_id"),
                merchant=t["merchant"],
                note=t.get("note", ""),
                occurred_at=datetime.fromisoformat(t["occurred_at"]),
                source=t.get("source", "manual"),
                created_at=datetime.fromisoformat(t["created_at"])
            )
            db.add(tx)
            
        # Insert budgets
        for b in data.get("budgets", []):
            bud = Budget(
                id=b["id"],
                category_id=b["category_id"],
                amount=b["amount"],
                period=b["period"],
                year=b["year"],
                month=b["month"]
            )
            db.add(bud)
            
    elif section == "books":
        # Delete existing
        books_result = await db.execute(select(Book).where(Book.user_id == user_id))
        books = books_result.scalars().all()
        book_ids = [b.id for b in books]
        
        if book_ids:
            await db.execute(delete(Highlight).where(Highlight.book_id.in_(book_ids)))
        await db.execute(delete(Book).where(Book.user_id == user_id))
        
        # Insert restored
        for b in data.get("books", []):
            book = Book(
                id=b["id"],
                user_id=user_id,
                title=b["title"],
                author=b["author"],
                status=b["status"],
                rating=b.get("rating"),
                started_at=datetime.fromisoformat(b["started_at"]) if b.get("started_at") else None,
                finished_at=datetime.fromisoformat(b["finished_at"]) if b.get("finished_at") else None,
                cover_url=b.get("cover_url"),
                created_at=datetime.fromisoformat(b["created_at"]),
                updated_at=datetime.fromisoformat(b["updated_at"])
            )
            db.add(book)
            
        for h in data.get("highlights", []):
            hl = Highlight(
                id=h["id"],
                book_id=h["book_id"],
                text=h["text"],
                location=h.get("location"),
                tags=h.get("tags"),
                created_at=datetime.fromisoformat(h["created_at"])
            )
            db.add(hl)
            
    elif section == "habits":
        # Delete existing
        habits_result = await db.execute(select(Habit).where(Habit.user_id == user_id))
        habits = habits_result.scalars().all()
        habit_ids = [h.id for h in habits]
        
        if habit_ids:
            await db.execute(delete(HabitLog).where(HabitLog.habit_id.in_(habit_ids)))
        await db.execute(delete(Habit).where(Habit.user_id == user_id))
        await db.execute(delete(JournalEntry).where(JournalEntry.user_id == user_id))
        
        # Insert restored
        for h in data.get("habits", []):
            habit = Habit(
                id=h["id"],
                user_id=user_id,
                name=h["name"],
                cadence=h["cadence"],
                target=h["target"],
                created_at=datetime.fromisoformat(h["created_at"]),
                updated_at=datetime.fromisoformat(h["updated_at"])
            )
            db.add(habit)
            
        for log_item in data.get("logs", []):
            log = HabitLog(
                id=log_item["id"],
                habit_id=log_item["habit_id"],
                date=datetime.fromisoformat(log_item["date"]).date(),
                value=log_item["value"]
            )
            db.add(log)
            
        for j in data.get("journal_entries", []):
            entry = JournalEntry(
                id=j["id"],
                user_id=user_id,
                body_json=j["body_json"],
                mood=j.get("mood"),
                created_at=datetime.fromisoformat(j["created_at"])
            )
            db.add(entry)
            
    await db.commit()
    return True


async def sync_section_background(user_id: str, section: str):
    from app.database import async_session_factory
    try:
        async with async_session_factory() as db:
            await _sync_section_to_gdrive_impl(user_id, section, db)
            await db.commit()
    except Exception as e:
        logger.error(f"Background sync failed for {section}: {e}")
