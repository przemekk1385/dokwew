"""empty message

Revision ID: 5eafbbecb810
Revises: 
Create Date: 2017-10-14 13:30:50.379452

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5eafbbecb810'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=15), nullable=False),
    sa.Column('signature_required', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_types_name'), 'types', ['name'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=10), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('meetings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('signature', sa.String(length=10), nullable=False),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meetings_signature'), 'meetings', ['signature'], unique=False)
    op.create_table('documents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('signature', sa.String(length=10), nullable=True),
    sa.Column('creation_date', sa.DateTime(), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=False),
    sa.Column('meeting_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ),
    sa.ForeignKeyConstraint(['type_id'], ['types.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_signature'), 'documents', ['signature'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_documents_signature'), table_name='documents')
    op.drop_table('documents')
    op.drop_index(op.f('ix_meetings_signature'), table_name='meetings')
    op.drop_table('meetings')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_types_name'), table_name='types')
    op.drop_table('types')
    # ### end Alembic commands ###
