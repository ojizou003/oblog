"""japan_tz

Revision ID: 213069fd9026
Revises: 788e7a5c3415
Create Date: 2024-10-09 19:03:53.322605

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '213069fd9026'
down_revision = '788e7a5c3415'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_posted', sa.DateTime(timezone=True), nullable=True))
        batch_op.drop_column('date_added')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_added', sa.DATETIME(), nullable=True))
        batch_op.drop_column('date_posted')

    # ### end Alembic commands ###
