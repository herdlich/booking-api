"""add username to users

Revision ID: aa2d2f97cc3a
Revises: 4d93591fb125
Create Date: 2026-09-26 08:01:32.512076

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'aa2d2f97cc3a'
down_revision: Union[str, Sequence[str], None] = '4d93591fb125'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('username', sa.String(length=50), nullable=True))

    op.execute(
        """
        UPDATE users
        SET username = 'user_' || user_id
        WHERE username IS NULL
        """
    )

    op.alter_column(
        "users",
        "username",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    op.create_unique_constraint(
        "uq_users_username",
        "users",
        ["username"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_users_username",
        "users",
        type_="unique",
    )

    op.drop_column('users', 'username')
