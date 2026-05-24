"""
chat_routes.py
~~~~~~~~~~~~~~
Blueprint:  /chat

Conversation CRUD (getters + setters)
--------------------------------------
GET  /chat/conversations                 → list all conversations for current user
POST /chat/conversations                 → create a new conversation  { title? }
GET  /chat/conversations/<id>            → get conversation + all messages
PUT  /chat/conversations/<id>            → rename conversation         { title }
DELETE /chat/conversations/<id>          → delete conversation (cascade messages)

Messaging
---------
POST /chat/conversations/<id>/messages
    Content-Type: multipart/form-data  OR  application/json

    Multipart fields:
        message   (str)          – user text (required if no file)
        file      (file)         – optional attachment
        model     (str)          – optional model override
        provider  (str)          – optional provider override (openrouter|anthropic|google)
        content   (str)          – optional separate text prompt to use alongside file

    JSON body:
        { "message": "...", "model": "...", "provider": "...", "content": "..." }

    The endpoint:
        1. If a file is attached → converts it to Markdown via Datalab API
        2. Builds the AI prompt (history + file context + user text)
        3. Streams the response back as Server-Sent Events
        4. Persists both the user message and the assembled AI reply to DB
"""

from __future__ import annotations

import json
import os

from flask import Blueprint, Response, current_app, jsonify, request

from app.extensions import db
from app.models.conversation import ChatMessage, Conversation
from app.services.ai_service import (
    AVAILABLE_PROVIDERS,
    DEFAULT_PROVIDER,
    DEFAULT_MODEL,
    get_ai_response,
)
from app.services.datalab_service import convert_file_to_markdown
from app.utils.decorators import current_user_required

# ---------------------------------------------------------------------------
# Blueprint setup
# ---------------------------------------------------------------------------

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")

_SYSTEM_PROMPT = (
    "You are a warm, caring, and expert pregnancy assistant. "
    "Answer in a supportive, reassuring, and professional tone. "
    "Always respond in the same language as the user. "
    "When a document or image is provided, its converted Markdown text will be "
    "prepended to the user's message — use it as context for your answer."
)

# MIME types accepted for file uploads
_ALLOWED_MIME_PREFIXES = (
    "image/",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats",
    "application/vnd.ms-",
    "text/",
)

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _get_conversation_or_404(conv_id: int, user_id: int):
    """Return the conversation or abort with 404."""
    conv = Conversation.query.filter_by(id=conv_id, user_id=user_id).first()
    if conv is None:
        return None
    return conv


def _build_history_messages(messages: list[ChatMessage]) -> list[dict]:
    """Convert stored ChatMessage rows to OpenAI-compatible dicts."""
    return [{"role": m.role, "content": m.content} for m in messages]


# ---------------------------------------------------------------------------
# Conversation CRUD  (getters & setters)
# ---------------------------------------------------------------------------


@chat_bp.route("/conversations", methods=["GET"])
@current_user_required
def list_conversations(current_user):
    """GET /chat/conversations — list all conversations (newest first)."""
    convs = (
        Conversation.query.filter_by(user_id=current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    return jsonify([c.to_dict() for c in convs]), 200


@chat_bp.route("/conversations", methods=["POST"])
@current_user_required
def create_conversation(current_user):
    """POST /chat/conversations — create a new conversation."""
    data = request.get_json(silent=True) or {}
    title = data.get("title", "New Conversation").strip() or "New Conversation"

    conv = Conversation(user_id=current_user.id, title=title)
    db.session.add(conv)
    db.session.commit()
    return jsonify(conv.to_dict()), 201


@chat_bp.route("/conversations/<int:conv_id>", methods=["GET"])
@current_user_required
def get_conversation(current_user, conv_id: int):
    """GET /chat/conversations/<id> — fetch conversation + all messages."""
    conv = _get_conversation_or_404(conv_id, current_user.id)
    if conv is None:
        return jsonify({"error": "Conversation not found"}), 404
    return jsonify(conv.to_dict(include_messages=True)), 200


@chat_bp.route("/conversations/<int:conv_id>", methods=["PUT"])
@current_user_required
def rename_conversation(current_user, conv_id: int):
    """PUT /chat/conversations/<id> — rename a conversation."""
    conv = _get_conversation_or_404(conv_id, current_user.id)
    if conv is None:
        return jsonify({"error": "Conversation not found"}), 404

    data = request.get_json(silent=True) or {}
    new_title = data.get("title", "").strip()
    if not new_title:
        return jsonify({"error": "title is required"}), 400

    conv.title = new_title
    db.session.commit()
    return jsonify(conv.to_dict()), 200


@chat_bp.route("/conversations/<int:conv_id>", methods=["DELETE"])
@current_user_required
def delete_conversation(current_user, conv_id: int):
    """DELETE /chat/conversations/<id> — delete conversation and all its messages."""
    conv = _get_conversation_or_404(conv_id, current_user.id)
    if conv is None:
        return jsonify({"error": "Conversation not found"}), 404

    db.session.delete(conv)
    db.session.commit()
    return jsonify({"message": "Conversation deleted"}), 200


# ---------------------------------------------------------------------------
# Messaging — with optional file upload → Datalab → Markdown
# ---------------------------------------------------------------------------


@chat_bp.route("/conversations/<int:conv_id>/messages", methods=["POST"])
@current_user_required
def send_message(current_user, conv_id: int):
    """
    POST /chat/conversations/<id>/messages

    Accepts multipart/form-data OR application/json.

    Multipart fields:
        message   (str)     – user's text message (required if no file)
        file      (file)    – optional document / image
        model     (str)     – optional model override
        provider  (str)     – optional provider: openrouter | anthropic | google
        content   (str)     – optional separate text prompt to combine with file

    JSON body:
        { "message": "...", "model": "...", "provider": "...", "content": "..." }

    If both a file and a text message/content are provided, the assistant
    receives the file's markdown followed by the separate text prompt,
    allowing it to answer questions about the document.

    Returns Server-Sent Events stream:
        data: {"token": "..."}
        data: [DONE]
    """
    conv = _get_conversation_or_404(conv_id, current_user.id)
    if conv is None:
        return jsonify({"error": "Conversation not found"}), 404

    # ------------------------------------------------------------------
    # 1. Parse request (supports both multipart and JSON)
    # ------------------------------------------------------------------
    content_type = request.content_type or ""

    if "multipart/form-data" in content_type:
        user_message = (request.form.get("message", "") or "").strip()
        model = (request.form.get("model", "") or DEFAULT_MODEL).strip()
        provider = (request.form.get("provider", "") or DEFAULT_PROVIDER).strip()
        content = (request.form.get("content", "") or "").strip()
        uploaded_file = request.files.get("file")
    else:
        body = request.get_json(silent=True) or {}
        user_message = (body.get("message", "") or "").strip()
        model = (body.get("model", "") or DEFAULT_MODEL).strip()
        provider = (body.get("provider", "") or DEFAULT_PROVIDER).strip()
        content = (body.get("content", "") or "").strip()
        uploaded_file = None

    if provider not in AVAILABLE_PROVIDERS:
        return (
            jsonify({"error": f"Invalid provider '{provider}'. Choose from: {', '.join(AVAILABLE_PROVIDERS)}"}),
            400,
        )

    if not user_message and uploaded_file is None:
        return jsonify({"error": "Provide at least a message or a file"}), 400

    # ------------------------------------------------------------------
    # 2. Convert file to Markdown via Datalab (if present)
    # ------------------------------------------------------------------
    attachment_name: str | None = None
    file_markdown: str | None = None

    if uploaded_file:
        mime_type = uploaded_file.mimetype or "application/octet-stream"
        if not any(mime_type.startswith(p) for p in _ALLOWED_MIME_PREFIXES):
            return (
                jsonify({"error": f"Unsupported file type: {mime_type}"}),
                415,
            )

        attachment_name = uploaded_file.filename
        file_bytes = uploaded_file.read()   # in-memory, never written to disk

        try:
            file_markdown = convert_file_to_markdown(
                file_bytes=file_bytes,
                filename=attachment_name,
                mime_type=mime_type,
                mode="balanced",
            )
        except RuntimeError as exc:
            return jsonify({"error": f"File conversion failed: {exc}"}), 502

    # ------------------------------------------------------------------
    # 3. Build prompt (system + history + current turn)
    # ------------------------------------------------------------------
    history_msgs = _build_history_messages(conv.messages)

    # Compose the user content: optional file context + separate text prompt
    parts: list[str] = []
    if file_markdown:
        parts.append(
            f"## Attached document: {attachment_name}\n\n{file_markdown}"
        )

    # Use "content" if provided (separate text prompt alongside file),
    # otherwise fall back to "message" for backward compatibility.
    # If both are present, combine them.
    user_text_parts: list[str] = []
    if content:
        user_text_parts.append(content)
    if user_message:
        user_text_parts.append(user_message)

    if user_text_parts:
        parts.append("\n\n".join(user_text_parts))

    full_user_content = "\n\n---\n\n".join(parts) if parts else "(no message)"

    # Persist user message to DB before streaming starts
    user_msg_row = ChatMessage(
        conversation_id=conv.id,
        role="user",
        content=full_user_content,
        attachment_name=attachment_name,
    )
    db.session.add(user_msg_row)

    # Auto-title: use a DB count so we don't rely on the stale in-memory list
    existing_count = ChatMessage.query.filter_by(conversation_id=conv.id).count()
    if existing_count == 0 and conv.title == "New Conversation":
        short_title = (user_message or content or attachment_name or "Chat")[:60]
        conv.title = short_title

    db.session.commit()

    messages_for_ai = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        *history_msgs,
        {"role": "user", "content": full_user_content},
    ]

    # ------------------------------------------------------------------
    # 4. Stream AI response as SSE, then persist to DB
    # ------------------------------------------------------------------
    app = current_app._get_current_object()  # capture before entering generator
    conv_id_capture = conv.id                # capture primitive, avoids detached-instance issues

    def generate():
        collected_tokens: list[str] = []
        stream_done = False
        try:
            stream = get_ai_response(
                messages=messages_for_ai,
                model=model,
                provider=provider,
            )
            for token in stream:
                collected_tokens.append(token)
                yield f"data: {json.dumps({'token': token})}\n\n"

            stream_done = True
            yield "data: [DONE]\n\n"

        except ValueError as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

        finally:
            # Always persist whatever tokens were collected, even on partial
            # streams caused by client disconnect or early errors.
            if collected_tokens:
                with app.app_context():
                    try:
                        assistant_row = ChatMessage(
                            conversation_id=conv_id_capture,
                            role="assistant",
                            content="".join(collected_tokens),
                        )
                        db.session.add(assistant_row)
                        db.session.commit()
                    except Exception:
                        db.session.rollback()

    return Response(generate(), mimetype="text/event-stream")
