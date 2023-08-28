"""events_data

Revision ID: 0c3144d48cd7
Revises: 3912e61cecf4
Create Date: 2023-03-29 16:46:18.868706

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0c3144d48cd7"
down_revision = "3912e61cecf4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("hash", sa.String(256), unique=True, nullable=False),
        sa.Column(
            "chat_id", sa.Integer, sa.ForeignKey("users.chat_id", ondelete="CASCADE")
        ),
        sa.Column(
            "update_interval",
            sa.Integer,
            sa.CheckConstraint("update_interval > 0"),
        ),
        sa.Column("last_update", sa.DateTime),
        sa.Column("function_id", sa.Integer),
        sa.Column("enabled", sa.Boolean, default=True),
    )


def downgrade() -> None:
    op.drop_table("events")
