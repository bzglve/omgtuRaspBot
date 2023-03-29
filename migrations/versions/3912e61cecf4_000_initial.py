"""000_initial

Revision ID: 3912e61cecf4
Revises: 
Create Date: 2023-03-29 13:25:04.733026

"""
from alembic import op

import sqlalchemy as sa

# from database.base import Event, User


# revision identifiers, used by Alembic.
revision = "3912e61cecf4"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("chat_id", sa.Integer, unique=True),
        sa.Column("group_id", sa.Integer),
    )


def downgrade() -> None:
    op.drop_table('users')
