"""add path in configuration

Revision ID: 22aca011d72c
Revises: 883861d7470c
Create Date: 2021-03-10 12:43:15.277455

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "22aca011d72c"
down_revision = "883861d7470c"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("configurations") as batch_op:
        batch_op.add_column(sa.Column("path", sa.String(), nullable=True))
    with op.batch_alter_table("descriptions") as batch_op:
        batch_op.alter_column("text", existing_type=sa.VARCHAR(), nullable=True)
    # ### commands auto generated by Alembic - please adjust! ###
    # op.add_column("configurations", sa.Column("path", sa.String(), nullable=True))
    # op.alter_column("descriptions", "text", existing_type=sa.VARCHAR(), nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("descriptions", "text", existing_type=sa.VARCHAR(), nullable=False)
    op.drop_column("configurations", "path")
    # ### end Alembic commands ###
