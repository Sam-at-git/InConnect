"""
Message API endpoints
"""

from typing import Annotated, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.crud.message import message as message_crud
from app.crud.conversation import conversation as conversation_crud
from app.schemas.message import (
    MessageSendRequest,
    MessageSendResponse,
    MessageResponse,
)
from app.schemas.common import APIResponse
from app.core.auth import get_current_user_id
from app.dependencies import DBSession
from app.core.exceptions import NotFoundError
from app.utils.wechat import wechat_client
from app.models.conversation import Conversation
from app.models.message import Message

router = APIRouter()


@router.get("/conversations", response_model=APIResponse[list])
async def list_conversations(
    db: DBSession,
    hotel_id: str | None = None,
    status: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> APIResponse[list]:
    """
    List conversations

    Args:
        db: Database session
        hotel_id: Filter by hotel ID
        status: Filter by status
        limit: Maximum records to return

    Returns:
        List of conversations
    """
    if hotel_id:
        convs = await conversation_crud.get_by_hotel(db, hotel_id, 0, limit)
    elif status == "active":
        convs = await conversation_crud.get_active(db, None, limit)
    else:
        convs = await conversation_crud.get_multi(db, 0, limit)

    return APIResponse(data=[{
        "id": c.id,
        "hotel_id": c.hotel_id,
        "guest_id": c.guest_id,
        "guest_name": c.guest_name,
        "status": c.status,
        "last_message_at": c.last_message_at.isoformat() if c.last_message_at else None,
    } for c in convs])


@router.get("/conversations/{conversation_id}/messages", response_model=APIResponse[list[MessageResponse]])
async def get_conversation_messages(
    conversation_id: str,
    db: DBSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> APIResponse[list[MessageResponse]]:
    """
    Get messages for a conversation

    Args:
        conversation_id: Conversation ID
        db: Database session
        limit: Maximum messages to return

    Returns:
        List of messages
    """
    conv = await conversation_crud.get(db, conversation_id)
    if not conv:
        raise NotFoundError("Conversation not found")

    messages = await message_crud.get_by_conversation(db, conversation_id, limit)
    return APIResponse(data=[MessageResponse.model_validate(m) for m in messages])


@router.post("/send", response_model=APIResponse[MessageSendResponse])
async def send_message(
    request: MessageSendRequest,
    db: DBSession,
    user_id: str = Depends(get_current_user_id),
) -> APIResponse[MessageSendResponse]:
    """
    Send message to guest

    Args:
        request: Message send request
        db: Database session
        user_id: Current user ID

    Returns:
        Send result
    """
    # Get conversation
    conv = await conversation_crud.get(db, request.conversation_id)
    if not conv:
        raise NotFoundError("Conversation not found")

    # Create message record
    message = await message_crud.create_message(
        db,
        request.conversation_id,
        request.message_type.value,
        "outbound",
        content=request.content,
        media_url=request.media_url,
        sender_id=user_id,
    )

    # Update conversation last_message_at
    from datetime import datetime
    from sqlalchemy import update
    await db.execute(
        update(Conversation)  # type: ignore
        .filter(Conversation.id == request.conversation_id)
        .values(last_message_at=datetime.utcnow())
    )
    await db.commit()

    # Send to WeChat
    try:
        wechat_result = await wechat_client.send_text_message(
            conv.guest_id,
            request.content,
        )

        if wechat_result.get("errcode") == 0:
            # Update message with WeChat msgid
            message.wechat_msg_id = wechat_result.get("msgid")
            await db.commit()

            return APIResponse(
                message="Message sent successfully",
                data=MessageSendResponse(
                    message_id=message.id,
                    status="sent",
                    wechat_msg_id=wechat_result.get("msgid"),
                ),
            )
        else:
            # Mark as failed
            return APIResponse(
                code=3001,
                message=f"WeChat API error: {wechat_result.get('errmsg')}",
                data=MessageSendResponse(
                    message_id=message.id,
                    status="failed",
                ),
            )
    except Exception as e:
        from app.core.logging import get_logger
        logger = get_logger("app.api.v1.messages")
        logger.error(
            "Failed to send message",
            exc_info=True,
            extra={"conversation_id": request.conversation_id},
        )
        return APIResponse(
            code=3001,
            message="Failed to send message",
            data=MessageSendResponse(
                message_id=message.id,
                status="failed",
            ),
        )


@router.post("/conversations/{conversation_id}/close", response_model=APIResponse)
async def close_conversation(
    conversation_id: str,
    db: DBSession,
    user_id: str = Depends(get_current_user_id),
) -> APIResponse:
    """
    Close a conversation

    Args:
        conversation_id: Conversation ID
        db: Database session
        user_id: Current user ID

    Returns:
        Success response
    """
    conv = await conversation_crud.get(db, conversation_id)
    if not conv:
        raise NotFoundError("Conversation not found")

    from app.models.conversation import ConversationStatus
    updated = await conversation_crud.update(
        db,
        conv,
        {"status": ConversationStatus.CLOSED.value},
    )

    return APIResponse(message="Conversation closed")


@router.get("/search", response_model=APIResponse[list[MessageResponse]])
async def search_messages(
    db: Session = Depends(DBSession),
    hotel_id: Annotated[str, Query(description="Hotel ID")] = ...,
    keyword: Annotated[Optional[str], Query(description="Keyword to search in content")] = None,
    conversation_id: Annotated[Optional[str], Query(description="Filter by conversation")] = None,
    message_type: Annotated[Optional[str], Query(description="Filter by message type")] = None,
    direction: Annotated[Optional[str], Query(description="Filter by direction")] = None,
    start_date: Annotated[Optional[str], Query(description="Start date (ISO format)")] = None,
    end_date: Annotated[Optional[str], Query(description="End date (ISO format)")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> APIResponse[list[MessageResponse]]:
    """
    Advanced message search with multiple filters

    Args:
        db: Database session
        hotel_id: Hotel ID for filtering
        keyword: Keyword to search in message content
        conversation_id: Filter by conversation ID
        message_type: Filter by message type
        direction: Filter by message direction
        start_date: Start date for filtering
        end_date: End date for filtering
        limit: Maximum results to return

    Returns:
        List of matching messages
    """
    # Get conversations for hotel
    from sqlalchemy import select, and_, or_

    conv_query = select(Conversation.id).where(Conversation.hotel_id == hotel_id)
    conversation_ids = [row[0] for row in db.execute(conv_query).all()]

    if not conversation_ids:
        return APIResponse(data=[])

    # Build query
    query = select(Message).where(Message.conversation_id.in_(conversation_ids))

    # Apply filters
    filters = []

    if keyword:
        filters.append(Message.content.ilike(f"%{keyword}%"))

    if conversation_id:
        filters.append(Message.conversation_id == conversation_id)

    if message_type:
        filters.append(Message.message_type == message_type)

    if direction:
        filters.append(Message.direction == direction)

    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            filters.append(Message.created_at >= start_dt)
        except ValueError:
            pass

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            filters.append(Message.created_at <= end_dt)
        except ValueError:
            pass

    if filters:
        query = query.where(and_(*filters))

    # Order by created_at desc
    query = query.order_by(Message.created_at.desc()).limit(limit)

    # Execute query
    results = db.execute(query).scalars().all()

    return APIResponse(data=[MessageResponse.model_validate(m) for m in results])


@router.get("/export")
async def export_messages(
    db: Session = Depends(DBSession),
    hotel_id: Annotated[str, Query(description="Hotel ID")] = ...,
    keyword: Annotated[Optional[str], Query(description="Keyword to search")] = None,
    conversation_id: Annotated[Optional[str], Query(description="Filter by conversation")] = None,
    start_date: Annotated[Optional[str], Query(description="Start date")] = None,
    end_date: Annotated[Optional[str], Query(description="End date")] = None,
) -> Response:
    """
    Export messages to CSV

    Args:
        db: Database session
        hotel_id: Hotel ID for filtering
        keyword: Optional keyword filter
        conversation_id: Optional conversation filter
        start_date: Optional start date
        end_date: Optional end date

    Returns:
        CSV file with message data
    """
    import csv
    from io import StringIO
    from sqlalchemy import select, and_

    # Get conversations for hotel
    conv_query = select(Conversation.id).where(Conversation.hotel_id == hotel_id)
    conversation_ids = [row[0] for row in db.execute(conv_query).all()]

    if not conversation_ids:
        return Response(
            content="",
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=messages_export.csv"},
        )

    # Build query
    query = select(Message, Conversation).join(
        Conversation, Message.conversation_id == Conversation.id
    ).where(Message.conversation_id.in_(conversation_ids))

    # Apply filters
    filters = []

    if keyword:
        filters.append(Message.content.ilike(f"%{keyword}%"))

    if conversation_id:
        filters.append(Message.conversation_id == conversation_id)

    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            filters.append(Message.created_at >= start_dt)
        except ValueError:
            pass

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            filters.append(Message.created_at <= end_dt)
        except ValueError:
            pass

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(Message.created_at.desc())

    # Execute query
    results = db.execute(query).all()

    # Generate CSV
    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "消息ID",
        "会话ID",
        "客人姓名",
        "消息类型",
        "方向",
        "内容",
        "发送者ID",
        "发送时间",
    ])

    # Write data
    for message, conversation in results:
        writer.writerow([
            message.id,
            message.conversation_id,
            conversation.guest_name,
            message.message_type,
            message.direction,
            (message.content or "")[:500],  # Limit content length
            message.sender_id or "",
            message.created_at.strftime("%Y-%m-%d %H:%M:%S") if message.created_at else "",
        ])

    csv_data = output.getvalue()

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=messages_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        },
    )

