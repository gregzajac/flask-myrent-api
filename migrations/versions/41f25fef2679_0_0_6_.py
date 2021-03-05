"""empty message

Revision ID: 41f25fef2679
Revises: 1c4eb544cea8
Create Date: 2020-11-20 18:25:54.105303

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "41f25fef2679"
down_revision = "1c4eb544cea8"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "pictures",
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("flat_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["flat_id"],
            ["flats.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("pictures")
    # ### end Alembic commands ###
