"""Resize meta value column

Revision ID: 25527d692d46
Revises: 709085f65102
Create Date: 2022-02-21 22:11:03.306330

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '25527d692d46'
down_revision = '709085f65102'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("meta") as bo:
        bo.alter_column("value", type_=sa.String(4096))


def downgrade():
    with op.batch_alter_table("meta") as bo:
        bo.alter_column("value", type_=sa.String(255))
