"""add uuid on Exams

Revision ID: 626dd0bf49d8
Revises: 6ec5029e7454
Create Date: 2025-10-06 09:41:38.320421

"""
from alembic import op
import sqlalchemy as sa
import uuid
from sqlalchemy.engine import Inspector


# revision identifiers, used by Alembic.
revision = '626dd0bf49d8'
down_revision = '6ec5029e7454'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Tambah kolom uuid nullable dulu
    with op.batch_alter_table('exams', schema=None) as batch_op:
        batch_op.add_column(sa.Column('uuid', sa.String(length=36), nullable=True))

    # 2. Isi uuid untuk data lama
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM exams"))
    for row in result:
        conn.execute(
            sa.text("UPDATE exams SET uuid = :uuid WHERE id = :id"),
            {"uuid": str(uuid.uuid4()), "id": row.id}
        )

    # 3. Set kolom jadi NOT NULL + UNIQUE
    with op.batch_alter_table('exams', schema=None) as batch_op:
        batch_op.alter_column('uuid', existing_type=sa.String(36), nullable=False)
        batch_op.create_unique_constraint("uq_exams_uuid", ['uuid'])


def downgrade():
    with op.batch_alter_table('exams', schema=None) as batch_op:
        batch_op.drop_constraint("uq_exams_uuid", type_="unique")
        batch_op.drop_column('uuid')

    # ### end Alembic commands ###
