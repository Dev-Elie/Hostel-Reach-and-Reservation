"""empty message

Revision ID: d11f336e2b8d
Revises: b602f684b185
Create Date: 2021-06-25 16:07:22.371665

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd11f336e2b8d'
down_revision = 'b602f684b185'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hostel', sa.Column('rooms', sa.String(length=100), nullable=False))
    op.drop_constraint('room_ibfk_1', 'room', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('room_ibfk_1', 'room', 'hostel', ['hostel_id'], ['id'])
    op.drop_column('hostel', 'rooms')
    # ### end Alembic commands ###