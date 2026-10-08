"""0001_initial_cloudmodx_schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-10-07 16:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='developer'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. modules table
    op.create_table(
        'modules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('technology', sa.String(length=100), nullable=False),
        sa.Column('architecture', sa.String(length=100), nullable=False),
        sa.Column('environment', sa.String(length=50), nullable=False, server_default='development'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('repository_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_modules_id'), 'modules', ['id'], unique=False)
    op.create_index(op.f('ix_modules_name'), 'modules', ['name'], unique=False)
    op.create_index(op.f('ix_modules_owner_id'), 'modules', ['owner_id'], unique=False)
    op.create_index(op.f('ix_modules_status'), 'modules', ['status'], unique=False)

    # 3. artifacts table
    op.create_table(
        'artifacts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('storage_provider', sa.String(length=50), nullable=False, server_default='local'),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column('size_bytes', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('checksum', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_artifacts_id'), 'artifacts', ['id'], unique=False)
    op.create_index(op.f('ix_artifacts_module_id'), 'artifacts', ['module_id'], unique=False)

    # 4. module_versions table
    op.create_table(
        'module_versions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('release_notes', sa.Text(), nullable=True),
        sa.Column('artifact_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['artifact_id'], ['artifacts.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_module_versions_id'), 'module_versions', ['id'], unique=False)
    op.create_index(op.f('ix_module_versions_module_id'), 'module_versions', ['module_id'], unique=False)
    op.create_index(op.f('ix_module_versions_version'), 'module_versions', ['version'], unique=False)
    op.create_index(op.f('ix_module_versions_artifact_id'), 'module_versions', ['artifact_id'], unique=False)

    # 5. deployments table
    op.create_table(
        'deployments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('version_id', sa.Integer(), nullable=False),
        sa.Column('environment', sa.String(length=50), nullable=False, server_default='dev'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='queued'),
        sa.Column('deployed_by', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['deployed_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['version_id'], ['module_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_deployments_id'), 'deployments', ['id'], unique=False)
    op.create_index(op.f('ix_deployments_module_id'), 'deployments', ['module_id'], unique=False)
    op.create_index(op.f('ix_deployments_version_id'), 'deployments', ['version_id'], unique=False)
    op.create_index(op.f('ix_deployments_status'), 'deployments', ['status'], unique=False)
    op.create_index(op.f('ix_deployments_deployed_by'), 'deployments', ['deployed_by'], unique=False)

    # 6. audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_resource_type'), 'audit_logs', ['resource_type'], unique=False)
    op.create_index(op.f('ix_audit_logs_resource_id'), 'audit_logs', ['resource_id'], unique=False)


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('deployments')
    op.drop_table('module_versions')
    op.drop_table('artifacts')
    op.drop_table('modules')
    op.drop_table('users')
