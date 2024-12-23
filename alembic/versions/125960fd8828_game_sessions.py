"""Game sessions

Revision ID: 125960fd8828
Revises: 5a6be3a77f7c
Create Date: 2024-11-30 18:35:26.156741

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '125960fd8828'
down_revision: Union[str, None] = '5a6be3a77f7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('game_high_score', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('weekly_high_score', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('daily_high_score', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('last_score_update', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'last_score_update')
    op.drop_column('users', 'daily_high_score')
    op.drop_column('users', 'weekly_high_score')
    op.drop_column('users', 'game_high_score')
    # ### end Alembic commands ###
