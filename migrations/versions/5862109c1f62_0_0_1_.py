"""empty message

Revision ID: 5862109c1f62
Revises: 
Create Date: 2020-10-26 11:47:10.090246

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5862109c1f62'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('landlords',
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('identifier', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('last_name', sa.String(length=100), nullable=False),
    sa.Column('phone', sa.String(length=50), nullable=False),
    sa.Column('address', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_landlords_identifier'), 'landlords', ['identifier'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_landlords_identifier'), table_name='landlords')
    op.drop_table('landlords')
    # ### end Alembic commands ###
