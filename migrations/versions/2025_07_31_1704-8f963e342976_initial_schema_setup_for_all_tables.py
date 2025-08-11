"""Initial schema setup for all tables

Revision ID: 8f963e342976
Revises:
Create Date: 2025-07-31 17:04:26.421038

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8f963e342976'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Create 'users' table ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("phone_number", sa.String(30), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("first_name", sa.String(50), nullable=True),
        sa.Column("last_name", sa.String(50), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("is_enable_notifications", sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column("is_profile_complete", sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users"))
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)

    # ### Create 'user_sessions' table ###
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('refresh_token_jti', sa.String(36), nullable=False),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(100), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_user_sessions_user_id_users'), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_user_sessions'))
    )
    op.create_index(op.f('ix_user_sessions_refresh_token_jti'), 'user_sessions', ['refresh_token_jti'], unique=True)
    op.create_index(op.f('ix_user_sessions_user_id'), 'user_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_sessions_is_active'), 'user_sessions', ['is_active'], unique=False)

    # ### Create 'pending_otps' table ###
    op.create_table(
        'pending_otps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('phone_number', sa.String(30), nullable=False),
        sa.Column('hashed_otp', sa.String(255), nullable=False),
        sa.Column('attempts_left', sa.Integer(), nullable=False, server_default=sa.text('3')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id', name=op.f("pk_pending_otps"))
    )
    op.create_index(op.f('ix_pending_otps_status'), 'pending_otps', ['status'], unique=False)
    op.create_index(op.f('ix_pending_otps_phone_number'), 'pending_otps', ['phone_number'], unique=False)
    op.create_index(op.f('ix_pending_otps_expires_at'), 'pending_otps', ['expires_at'], unique=False)


def downgrade() -> None:
    # Drop in reverse order of creation, also dropping indexes first
    op.drop_index(op.f('ix_pending_otps_expires_at'), table_name='pending_otps')
    op.drop_index(op.f('ix_pending_otps_phone_number'), table_name='pending_otps')
    op.drop_index(op.f('ix_pending_otps_status'), table_name='pending_otps')
    op.drop_table('pending_otps')

    op.drop_index(op.f('ix_user_sessions_is_active'), table_name='user_sessions')
    op.drop_index(op.f('ix_user_sessions_user_id'), table_name='user_sessions')
    op.drop_index(op.f('ix_user_sessions_refresh_token_jti'), table_name='user_sessions')
    op.drop_table('user_sessions')

    op.drop_index(op.f('ix_users_phone_number'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
