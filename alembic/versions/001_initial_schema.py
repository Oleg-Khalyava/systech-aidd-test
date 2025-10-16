"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-10-16

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NULL,
            first_name TEXT NOT NULL,
            current_role TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP NULL
        )
    """)

    # Create messages table
    op.execute("""
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            length INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Create index for messages
    op.execute("""
        CREATE INDEX idx_messages_user_created
        ON messages(user_id, created_at)
    """)

    # Create FTS5 virtual table for full-text search
    op.execute("""
        CREATE VIRTUAL TABLE messages_fts
        USING fts5(content, content='messages', content_rowid='id')
    """)

    # Create trigger to sync INSERT
    op.execute("""
        CREATE TRIGGER messages_fts_insert AFTER INSERT ON messages BEGIN
            INSERT INTO messages_fts(rowid, content)
            VALUES (new.id, new.content);
        END
    """)

    # Create trigger to sync UPDATE
    op.execute("""
        CREATE TRIGGER messages_fts_update AFTER UPDATE ON messages BEGIN
            UPDATE messages_fts
            SET content = new.content
            WHERE rowid = new.id;
        END
    """)

    # Create trigger to sync DELETE
    op.execute("""
        CREATE TRIGGER messages_fts_delete AFTER DELETE ON messages BEGIN
            DELETE FROM messages_fts WHERE rowid = old.id;
        END
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS messages_fts_delete")
    op.execute("DROP TRIGGER IF EXISTS messages_fts_update")
    op.execute("DROP TRIGGER IF EXISTS messages_fts_insert")

    # Drop FTS table
    op.execute("DROP TABLE IF EXISTS messages_fts")

    # Drop index
    op.execute("DROP INDEX IF EXISTS idx_messages_user_created")

    # Drop tables
    op.execute("DROP TABLE IF EXISTS messages")
    op.execute("DROP TABLE IF EXISTS users")

