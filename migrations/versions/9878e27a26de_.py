"""empty message

Revision ID: 9878e27a26de
Revises: 6638fdeaf7e0
Create Date: 2017-10-15 19:01:50.706978

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9878e27a26de'
down_revision = '6638fdeaf7e0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('documents', sa.Column('description', sa.String(length=100), nullable=True))
    op.create_index(op.f('ix_documents_description'), 'documents', ['description'], unique=False)
    op.add_column('types', sa.Column('standlone', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('types', 'standlone')
    op.drop_index(op.f('ix_documents_description'), table_name='documents')
    op.drop_column('documents', 'description')
    # ### end Alembic commands ###