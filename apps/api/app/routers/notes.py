import json
import re

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import delete, select

from app.deps import DB, CurrentUser
from app.gdrive_sync import sync_section_to_gdrive
from app.models.notes import Note, NoteLink

router = APIRouter(prefix="/api/notes", tags=["Notes"])


class NoteUpdate(BaseModel):
    title: str
    body_json: str
    tags: str | None = None


@router.get("")
async def list_notes(current_user: CurrentUser, db: DB, q: str | None = None):
    query = select(Note).where(Note.user_id == current_user.id)
    if q:
        # Case-insensitive search on title or body content
        query = query.where(Note.title.ilike(f"%{q}%") | Note.body_json.ilike(f"%{q}%"))

    query = query.order_by(Note.updated_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_note(current_user: CurrentUser, db: DB):
    note = Note(
        user_id=current_user.id,
        title="Untitled Note",
        body_json=json.dumps({"text": ""}),
        tags="",
    )
    db.add(note)
    await db.flush()
    await db.refresh(note)
    await sync_section_to_gdrive(current_user.id, "notes", db)
    return note


@router.get("/{note_id}")
async def get_note(note_id: str, current_user: CurrentUser, db: DB):
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Fetch backlinks: other notes that reference this note
    backlink_query = (
        select(Note)
        .join(NoteLink, NoteLink.from_note_id == Note.id)
        .where(NoteLink.to_note_id == note_id, Note.user_id == current_user.id)
    )
    backlink_result = await db.execute(backlink_query)
    backlinks = backlink_result.scalars().all()

    return {
        "id": note.id,
        "title": note.title,
        "body_json": note.body_json,
        "tags": note.tags,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
        "backlinks": [{"id": n.id, "title": n.title} for n in backlinks],
    }


@router.put("/{note_id}")
async def update_note(
    note_id: str, body: NoteUpdate, current_user: CurrentUser, db: DB
):
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note.title = body.title
    note.body_json = body.body_json
    note.tags = body.tags

    # Parse backlinks: Obsidian-style [[Note Title]] in the body text
    text_content = ""
    try:
        data = json.loads(body.body_json)
        text_content = data.get("text", "")
    except Exception:
        text_content = body.body_json

    links = re.findall(r"\[\[(.*?)\]\]", text_content)

    # Delete existing outgoing links for this note
    await db.execute(delete(NoteLink).where(NoteLink.from_note_id == note_id))

    # Resolve target titles to note IDs and create links
    unique_links = list(set([link.strip() for link in links if link.strip()]))
    for target_title in unique_links:
        # Find target note by title (case-insensitive) for the same user
        target_result = await db.execute(
            select(Note).where(
                Note.title.ilike(target_title),
                Note.user_id == current_user.id,
                Note.id != note_id,  # Don't link to self
            )
        )
        target_note = target_result.scalar_one_or_none()
        if target_note:
            new_link = NoteLink(from_note_id=note_id, to_note_id=target_note.id)
            db.add(new_link)

    await db.flush()
    await db.refresh(note)
    await sync_section_to_gdrive(current_user.id, "notes", db)
    return note


@router.delete("/{note_id}")
async def delete_note(note_id: str, current_user: CurrentUser, db: DB):
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    await db.delete(note)
    await sync_section_to_gdrive(current_user.id, "notes", db)
    return {"status": "success"}
