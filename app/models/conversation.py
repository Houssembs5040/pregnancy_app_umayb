from datetime import datetime
from app.extensions import db


class Conversation(db.Model):
    """A named chat session belonging to a user."""

    __tablename__ = "conversations"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    user_id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = db.Column(db.String(255), nullable=False, default="New Conversation")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    messages = db.relationship(
        "ChatMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    def to_dict(self, include_messages: bool = False) -> dict:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_messages:
            data["messages"] = [m.to_dict() for m in self.messages]
        return data


class ChatMessage(db.Model):
    """A single turn (user or assistant) inside a Conversation."""

    __tablename__ = "chat_messages"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    conversation_id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        db.ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = db.Column(db.String(20), nullable=False)  # 'user' | 'assistant'
    content = db.Column(db.Text, nullable=False)
    # Optional: store the file name that was attached (no binary stored)
    attachment_name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    conversation = db.relationship("Conversation", back_populates="messages")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "attachment_name": self.attachment_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
