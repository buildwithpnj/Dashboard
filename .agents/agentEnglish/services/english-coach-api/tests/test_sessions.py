import pytest
import uuid
from app.db.session import AsyncSessionLocal
from app.db.models import Session, Message
from app.repositories.sessions import SessionsRepository
from app.repositories.messages import MessagesRepository

@pytest.mark.anyio
async def test_session_and_message_repositories():
    """Verifies that chat sessions and associated messages persist in the DB."""
    async with AsyncSessionLocal() as session:
        sess_repo = SessionsRepository(session)
        msg_repo = MessagesRepository(session)

        user_id = f"user-{uuid.uuid4()}"
        sess_id = f"sess-{uuid.uuid4()}"

        # 1. Create and save active session
        sess = Session(
            id=sess_id,
            user_id=user_id,
            product_id="english_coach",
            is_active=True
        )
        await sess_repo.create(sess)

        fetched_sess = await sess_repo.get_active_by_user_and_product(user_id, "english_coach")
        assert fetched_sess is not None
        assert fetched_sess.id == sess_id

        # 2. Add message to session
        msg_id = f"msg-{uuid.uuid4()}"
        msg = Message(
            id=msg_id,
            session_id=sess_id,
            role="user",
            content="Hello English Coach",
            metadata_json="{}"
        )
        await msg_repo.create(msg)

        # 3. Read messages list from session
        messages = await msg_repo.get_by_session(sess_id)
        assert len(messages) == 1
        assert messages[0].id == msg_id
        assert messages[0].content == "Hello English Coach"

        await session.rollback()
