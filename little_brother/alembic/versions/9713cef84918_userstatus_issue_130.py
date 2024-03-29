"""UserStatus_Issue_130

Revision ID: 9713cef84918
Revises: e0c0d7048235
Create Date: 2021-06-12 18:14:02.135595

"""
import sqlalchemy as sa
from alembic import op

from little_brother import constants

# revision identifiers, used by Alembic.

revision = '9713cef84918'
down_revision = 'e0c0d7048235'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_status',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('optional_time_used', sa.Integer(), nullable=False),
                    sa.Column('reference_date', sa.Date(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.add_column('ruleset', sa.Column('optional_time_per_day', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('access_code', sa.String(length=256), nullable=True))

    # manually added:
    op.execute('UPDATE user SET access_code = "{value}"'.format(value=constants.DEFAULT_ACCESS_CODE))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'access_code')
    op.drop_column('ruleset', 'optional_time_per_day')
    op.drop_table('user_status')
    # ### end Alembic commands ###
