"""Add committed_shifts and guarantee_logs tables

Priority 2: Income Guarantee Window

Creates tables for:
- committed_shifts: Tracks driver shift commitments with earnings and guarantee data
- guarantee_logs: Audit trail for all guarantee events (FR13, NFR11)

Revision ID: b2f8a1c3d4e5
Revises: e6f6ba83c2dc
Create Date: 2026-02-13
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b2f8a1c3d4e5'
down_revision = '4706429fab17'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === COMMITTED SHIFTS TABLE ===
    op.create_table(
        'committed_shifts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),

        # Driver reference
        sa.Column('driver_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),

        # Shift details
        sa.Column('location_name', sa.String(256), nullable=False),
        sa.Column('location_key', sa.String(128), nullable=True),
        sa.Column('region', sa.String(128), nullable=True),
        sa.Column('zone', sa.String(128), nullable=True),
        sa.Column('shift_type', sa.String(128), nullable=False),
        sa.Column('day_name', sa.String(20), nullable=True),

        # Time window
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),

        # Earnings
        sa.Column('predicted_earnings', sa.Float(), nullable=False),
        sa.Column('actual_earnings', sa.Float(), nullable=True),
        sa.Column('base_hourly_rate', sa.Float(), nullable=True),
        sa.Column('demand_score', sa.Float(), nullable=True),

        # Income guarantee
        sa.Column('guarantee_eligible', sa.Boolean(), default=True),
        sa.Column('guarantee_threshold', sa.Float(), default=0.9),
        sa.Column('guaranteed_minimum', sa.Float(), nullable=True),
        sa.Column('topup_amount', sa.Float(), default=0.0),
        sa.Column('guarantee_activated', sa.Boolean(), default=False),

        # Status & lifecycle
        sa.Column('status', sa.String(20), default='committed'),
        sa.Column('commitment_time', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),

        # Metadata
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # === GUARANTEE LOGS TABLE (FR13 + NFR11) ===
    op.create_table(
        'guarantee_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),

        # References
        sa.Column('committed_shift_id', sa.Integer(), sa.ForeignKey('committed_shifts.id'), nullable=False, index=True),
        sa.Column('driver_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),

        # Event details
        sa.Column('event_type', sa.String(64), nullable=False),
        sa.Column('event_description', sa.String(512), nullable=True),

        # Financial snapshot
        sa.Column('predicted_earnings', sa.Float(), nullable=True),
        sa.Column('actual_earnings', sa.Float(), nullable=True),
        sa.Column('guaranteed_minimum', sa.Float(), nullable=True),
        sa.Column('topup_amount', sa.Float(), nullable=True),
        sa.Column('guarantee_threshold', sa.Float(), nullable=True),

        # Eligibility snapshot
        sa.Column('was_eligible', sa.Boolean(), nullable=True),
        sa.Column('eligibility_reason', sa.String(256), nullable=True),

        # Metadata
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('ip_address', sa.String(45), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('guarantee_logs')
    op.drop_table('committed_shifts')
