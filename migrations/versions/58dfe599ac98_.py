"""empty message

Revision ID: 58dfe599ac98
Revises: d4638d27d3e5
Create Date: 2021-06-25 13:42:50.726347

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '58dfe599ac98'
down_revision = 'd4638d27d3e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('hostel', 'place')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hostel', sa.Column('place', mysql.TEXT(), nullable=False))
    # ### end Alembic commands ###
