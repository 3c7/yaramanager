"""Init

Revision ID: 892f53ea8054
Revises: 
Create Date: 2021-03-29 21:38:23.372145

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '892f53ea8054'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rule',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('condition', sa.Text(), nullable=True),
    sa.Column('imports', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rule_id'), 'rule', ['id'], unique=False)
    op.create_index(op.f('ix_rule_name'), 'rule', ['name'], unique=False)
    op.create_table('tag',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tag_id'), 'tag', ['id'], unique=False)
    op.create_index(op.f('ix_tag_name'), 'tag', ['name'], unique=False)
    op.create_table('meta',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('key', sa.String(length=255), nullable=True),
    sa.Column('value', sa.String(length=255), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('rule_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['rule_id'], ['rule.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meta_id'), 'meta', ['id'], unique=False)
    op.create_index(op.f('ix_meta_key'), 'meta', ['key'], unique=False)
    op.create_index(op.f('ix_meta_value'), 'meta', ['value'], unique=False)
    op.create_table('string',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('type', sa.String(length=5), nullable=True),
    sa.Column('value', sa.Text(), nullable=True),
    sa.Column('modifiers', sa.Integer(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('rule_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['rule_id'], ['rule.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_string_id'), 'string', ['id'], unique=False)
    op.create_index(op.f('ix_string_name'), 'string', ['name'], unique=False)
    op.create_table('tags_rules',
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.Column('rule_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['rule_id'], ['rule.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tags_rules')
    op.drop_index(op.f('ix_string_name'), table_name='string')
    op.drop_index(op.f('ix_string_id'), table_name='string')
    op.drop_table('string')
    op.drop_index(op.f('ix_meta_value'), table_name='meta')
    op.drop_index(op.f('ix_meta_key'), table_name='meta')
    op.drop_index(op.f('ix_meta_id'), table_name='meta')
    op.drop_table('meta')
    op.drop_index(op.f('ix_tag_name'), table_name='tag')
    op.drop_index(op.f('ix_tag_id'), table_name='tag')
    op.drop_table('tag')
    op.drop_index(op.f('ix_rule_name'), table_name='rule')
    op.drop_index(op.f('ix_rule_id'), table_name='rule')
    op.drop_table('rule')
    # ### end Alembic commands ###
