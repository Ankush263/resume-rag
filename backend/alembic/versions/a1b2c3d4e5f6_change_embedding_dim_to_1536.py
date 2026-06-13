"""change document_chunks embedding dimension to 1536

Revision ID: a1b2c3d4e5f6
Revises: 0ae06507cfcf
Create Date: 2026-06-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '0ae06507cfcf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop any existing embeddings first: dimensions are incompatible and
    # there is no meaningful way to convert 3072-dim vectors to 1536-dim.
    op.execute('UPDATE document_chunks SET embedding = NULL')
    op.alter_column(
        'document_chunks',
        'embedding',
        type_=Vector(1536),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('UPDATE document_chunks SET embedding = NULL')
    op.alter_column(
        'document_chunks',
        'embedding',
        type_=Vector(3072),
        existing_nullable=True,
    )
