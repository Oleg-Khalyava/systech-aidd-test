"""remove_current_role_from_users

Revision ID: 59aea0b85086
Revises: 001
Create Date: 2025-10-16 15:47:59.572808

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "59aea0b85086"
down_revision: Union[str, Sequence[str], None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove current_role column from users table.

    SQLite doesn't support DROP COLUMN directly, so we need to:
    1. Create new table without current_role
    2. Copy data
    3. Drop old table
    4. Rename new table
    """
    # Create new users table without current_role
    op.execute(
        """
        CREATE TABLE users_new (
            id INTEGER PRIMARY KEY,
            username TEXT NULL,
            first_name TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP NULL
        )
    """
    )

    # Copy data from old table to new (excluding current_role)
    op.execute(
        """
        INSERT INTO users_new (id, username, first_name, created_at, last_accessed, deleted_at)
        SELECT id, username, first_name, created_at, last_accessed, deleted_at
        FROM users
    """
    )

    # Drop old table
    op.execute("DROP TABLE users")

    # Rename new table to users
    op.execute("ALTER TABLE users_new RENAME TO users")


def downgrade() -> None:
    """Add current_role column back to users table."""
    # Create new users table with current_role
    op.execute(
        """
        CREATE TABLE users_new (
            id INTEGER PRIMARY KEY,
            username TEXT NULL,
            first_name TEXT NOT NULL,
            current_role TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP NULL
        )
    """
    )

    # Copy data from old table to new (adding empty current_role)
    op.execute(
        """
        INSERT INTO users_new (id, username, first_name, current_role, created_at, last_accessed, deleted_at)
        SELECT id, username, first_name, '', created_at, last_accessed, deleted_at
        FROM users
    """
    )

    # Drop old table
    op.execute("DROP TABLE users")

    # Rename new table to users
    op.execute("ALTER TABLE users_new RENAME TO users")
