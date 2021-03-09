"""empty message

Revision ID: 883861d7470c
Revises: 00025b43df96
Create Date: 2021-03-09 10:03:00.200694

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '883861d7470c'
down_revision = '00025b43df96'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('description',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('shop')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shop',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('shop', sa.VARCHAR(length=255), nullable=True),
    sa.Column('token', sa.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('description')
    # ### end Alembic commands ###
