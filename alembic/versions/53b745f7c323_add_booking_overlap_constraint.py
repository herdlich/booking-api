"""add booking overlap constraint

Revision ID: 53b745f7c323
Revises: 68f4798e5907
Create Date: 2026-08-30 14:46:20.746276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53b745f7c323'
down_revision: Union[str, Sequence[str], None] = '68f4798e5907'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    op.execute("""
        ALTER TABLE bookings
        ADD CONSTRAINT no_overlapping_bookings
        EXCLUDE USING gist (
            room_id WITH =,
            tsrange(start_at, end_at, '[)') WITH &&
        )
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "no_overlapping_bookings",
        "bookings"
    )
