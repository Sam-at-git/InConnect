"""
WeChat Webhook for receiving messages
"""

import json
from typing import Any

from fastapi import APIRouter, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.conversation import conversation as conversation_crud
from app.crud.message import message as message_crud
from app.schemas.conversation import ConversationCreate
from app.core.logging import get_logger
from app.dependencies import get_db_session
from app.models.conversation import Conversation
from app.models.message import Message

router = APIRouter()
logger = get_logger("app.api.v1.webhook")


@router.post("/wechat", status_code=200)
async def wechat_webhook(
    request: Request,
) -> dict[str, str]:
    """
    WeChat webhook endpoint for receiving messages

    This endpoint receives messages from WeChat Work (企业微信)
    and processes them to create conversations and messages.

    Args:
        request: FastAPI request

    Returns:
        Success response
    """
    from app.dependencies import get_db_session

    db = await anext(get_db_session())

    try:
        # Get raw body
        body = await request.body()
        data = json.loads(body)

        logger.info(
            "Received WeChat webhook",
            extra={"event_type": data.get("event_type", "unknown")},
        )

        # Parse message data
        msg_type = data.get("msgtype")
        from_user = data.get("from_user", {}).get("userid")
        to_user = data.get("to_user", {}).get("userid")
        agent_id = data.get("agentid")

        # For MVP, we'll use a simplified approach
        # In production, you would verify the signature
        # and handle different message types properly

        if msg_type == "text":
            content = data.get("content", "")
            message = await _handle_text_message(
                db,
                from_user,
                to_user,
                agent_id,
                content,
                data.get("msgid"),
            )

            # Check for auto-ticket creation
            if message:
                from app.services.auto_ticket_service import auto_ticket_service
                if await auto_ticket_service.should_create_ticket(db, message):
                    await auto_ticket_service.create_ticket_from_message(db, message)

        elif msg_type == "image":
            media_id = data.get("media_id")
            await _handle_media_message(
                db,
                from_user,
                to_user,
                agent_id,
                "image",
                media_id,
                data.get("msgid"),
            )
        elif msg_type == "voice":
            media_id = data.get("media_id")
            await _handle_media_message(
                db,
                from_user,
                to_user,
                agent_id,
                "voice",
                media_id,
                data.get("msgid"),
            )

        return {"errcode": 0, "errmsg": "ok"}

    except Exception as e:
        logger.error(
            "Error processing WeChat webhook",
            exc_info=True,
            extra={"error": str(e)},
        )
        # Return success anyway to avoid retry loops
        return {"errcode": 0, "errmsg": "ok"}
    finally:
        await db.close()


async def _handle_text_message(
    db: AsyncSession,
    from_user: str,
    to_user: str | None,
    agent_id: str | None,
    content: str,
    msg_id: str | None,
) -> Message | None:
    """
    Handle text message from WeChat

    Args:
        db: Database session
        from_user: Sender user ID
        to_user: Recipient user ID
        agent_id: Agent ID
        content: Message content
        msg_id: WeChat message ID
    """
    from datetime import datetime

    # Check for duplicate messages
    if msg_id:
        existing = await message_crud.get_by_wechat_msg_id(db, msg_id)
        if existing:
            logger.info("Duplicate message ignored", extra={"msg_id": msg_id})
            return

    # Get or create conversation
    hotel_id = agent_id or "default_hotel"

    conv = await conversation_crud.get_by_guest_and_hotel(
        db, hotel_id, from_user
    )

    if not conv:
        conv_data = ConversationCreate(
            hotel_id=hotel_id,
            guest_id=from_user,
            status="active",
        )
        conv = await conversation_crud.create(db, conv_data)
        logger.info("Created new conversation", extra={"conversation_id": conv.id})

    # Create message
    await message_crud.create_message(
        db,
        conv.id,
        "text",
        "inbound",
        content=content,
        sender_id=from_user,
        wechat_msg_id=msg_id,
    )

    # Update conversation
    from sqlalchemy import update
    await db.execute(
        update(Conversation)  # type: ignore
        .filter(Conversation.id == conv.id)
        .values(last_message_at=datetime.utcnow())
    )
    await db.commit()

    logger.info(
        "Text message processed",
        extra={"conversation_id": conv.id, "guest_id": from_user},
    )

    # Get the message for auto-ticket processing
    from app.models.message import Message
    msg_result = await db.execute(
        select(Message)
        .filter(Message.conversation_id == conv.id)
        .order_by(Message.created_at.desc())
        .limit(1)
    )
    return msg_result.scalar_one_or_none()


async def _handle_media_message(
    db: AsyncSession,
    from_user: str,
    to_user: str | None,
    agent_id: str | None,
    media_type: str,
    media_id: str,
    msg_id: str | None,
) -> None:
    """
    Handle media message (image/voice) from WeChat

    Args:
        db: Database session
        from_user: Sender user ID
        to_user: Recipient user ID
        agent_id: Agent ID
        media_type: Type of media (image/voice)
        media_id: WeChat media ID
        msg_id: WeChat message ID
    """
    from datetime import datetime

    # Check for duplicate
    if msg_id:
        existing = await message_crud.get_by_wechat_msg_id(db, msg_id)
        if existing:
            return

    hotel_id = agent_id or "default_hotel"

    conv = await conversation_crud.get_by_guest_and_hotel(
        db, hotel_id, from_user
    )

    if not conv:
        conv_data = ConversationCreate(
            hotel_id=hotel_id,
            guest_id=from_user,
            status="active",
        )
        conv = await conversation_crud.create(db, conv_data)

    # In production, download media from WeChat and store in object storage
    media_url = f"wechat://{media_type}/{media_id}"

    await message_crud.create_message(
        db,
        conv.id,
        media_type,
        "inbound",
        media_url=media_url,
        sender_id=from_user,
        wechat_msg_id=msg_id,
    )

    # Update conversation
    from sqlalchemy import update
    await db.execute(
        update(Conversation)  # type: ignore
        .filter(Conversation.id == conv.id)
        .values(last_message_at=datetime.utcnow())
    )
    await db.commit()
