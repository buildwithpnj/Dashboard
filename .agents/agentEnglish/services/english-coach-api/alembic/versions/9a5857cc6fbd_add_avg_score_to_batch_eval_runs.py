"""Add avg_score to batch_eval_runs

Revision ID: 9a5857cc6fbd
Revises: 66aec351cb57
Create Date: 2026-07-12 13:39:04.567016

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a5857cc6fbd'
down_revision: Union[str, Sequence[str], None] = '66aec351cb57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('batch_eval_runs', sa.Column('avg_score', sa.Float(), nullable=False, server_default='0.0'))

def downgrade() -> None:
    op.drop_column('batch_eval_runs', 'avg_score')
