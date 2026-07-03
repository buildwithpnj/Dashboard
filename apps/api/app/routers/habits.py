import json
from datetime import date

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.deps import DB, CurrentUser
from app.gdrive_sync import sync_section_to_gdrive
from app.models.habits import Habit, HabitLog, JournalEntry

router = APIRouter(prefix="/api/habits", tags=["Habits"])


class HabitCreate(BaseModel):
    name: str
    cadence: str = "daily"
    target: int = 1


class HabitUpdate(BaseModel):
    name: str
    cadence: str
    target: int


class LogHabitRequest(BaseModel):
    date: date
    value: float


class JournalUpdate(BaseModel):
    body_json: str
    mood: int | None = None


# ─── Habits Endpoints ───────────────────────────────────────

@router.get("")
async def list_habits(current_user: CurrentUser, db: DB):
    result = await db.execute(
        select(Habit)
        .where(Habit.user_id == current_user.id)
        .order_by(Habit.created_at.desc())
    )
    habits = result.scalars().all()

    res = []
    for h in habits:
        log_res = await db.execute(
            select(HabitLog).where(HabitLog.habit_id == h.id)
        )
        logs = log_res.scalars().all()
        res.append({
            "id": h.id,
            "name": h.name,
            "cadence": h.cadence,
            "target": h.target,
            "created_at": h.created_at,
            "updated_at": h.updated_at,
            "logs": [{"date": log.date.isoformat(), "value": float(log.value)} for log in logs],
        })
    return res


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_habit(body: HabitCreate, current_user: CurrentUser, db: DB):
    habit = Habit(
        user_id=current_user.id,
        name=body.name,
        cadence=body.cadence,
        target=body.target,
    )
    db.add(habit)
    await db.flush()
    await db.refresh(habit)
    await sync_section_to_gdrive(current_user.id, "habits", db)
    return habit


@router.put("/{habit_id}")
async def update_habit(
    habit_id: str, body: HabitUpdate, current_user: CurrentUser, db: DB
):
    result = await db.execute(
        select(Habit).where(Habit.id == habit_id, Habit.user_id == current_user.id)
    )
    habit = result.scalar_one_or_none()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    habit.name = body.name
    habit.cadence = body.cadence
    habit.target = body.target

    await db.flush()
    await db.refresh(habit)
    await sync_section_to_gdrive(current_user.id, "habits", db)
    return habit


@router.delete("/{habit_id}")
async def delete_habit(habit_id: str, current_user: CurrentUser, db: DB):
    result = await db.execute(
        select(Habit).where(Habit.id == habit_id, Habit.user_id == current_user.id)
    )
    habit = result.scalar_one_or_none()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    await db.delete(habit)
    await sync_section_to_gdrive(current_user.id, "habits", db)
    return {"status": "success"}


@router.post("/{habit_id}/log")
async def log_habit(
    habit_id: str, body: LogHabitRequest, current_user: CurrentUser, db: DB
):
    result = await db.execute(
        select(Habit).where(Habit.id == habit_id, Habit.user_id == current_user.id)
    )
    habit = result.scalar_one_or_none()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    log_res = await db.execute(
        select(HabitLog)
        .where(HabitLog.habit_id == habit_id, HabitLog.date == body.date)
    )
    log = log_res.scalar_one_or_none()

    if body.value <= 0:
        if log:
            await db.delete(log)
    else:
        if log:
            log.value = body.value
        else:
            log = HabitLog(
                habit_id=habit_id,
                date=body.date,
                value=body.value,
            )
            db.add(log)

    await sync_section_to_gdrive(current_user.id, "habits", db)
    return {"status": "success"}


# ─── Journal Endpoints ──────────────────────────────────────

@router.get("/journal/list")
async def list_journal(current_user: CurrentUser, db: DB):
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.user_id == current_user.id)
        .order_by(JournalEntry.created_at.desc())
    )
    return result.scalars().all()


@router.post("/journal", status_code=status.HTTP_201_CREATED)
async def create_journal(current_user: CurrentUser, db: DB):
    entry = JournalEntry(
        user_id=current_user.id,
        body_json=json.dumps({"text": ""}),
        mood=3,
    )
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    await sync_section_to_gdrive(current_user.id, "habits", db)
    return entry


@router.put("/journal/{journal_id}")
async def update_journal(
    journal_id: str, body: JournalUpdate, current_user: CurrentUser, db: DB
):
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.id == journal_id, JournalEntry.user_id == current_user.id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    entry.body_json = body.body_json
    entry.mood = body.mood

    await db.flush()
    await db.refresh(entry)
    await sync_section_to_gdrive(current_user.id, "habits", db)
    return entry


@router.delete("/journal/{journal_id}")
async def delete_journal(journal_id: str, current_user: CurrentUser, db: DB):
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.id == journal_id, JournalEntry.user_id == current_user.id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    await db.delete(entry)
    await sync_section_to_gdrive(current_user.id, "habits", db)
    return {"status": "success"}
