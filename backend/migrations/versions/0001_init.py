from alembic import op
import sqlalchemy as sa

revision = '0001_init'
down_revision = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('full_name', sa.String(120), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_prt_token_hash', 'password_reset_tokens', ['token_hash'])

    op.create_table(
        'predictions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('headline', sa.Text(), nullable=False),
        sa.Column('article_content', sa.Text(), nullable=False),
        sa.Column('ml_prediction', sa.String(30), nullable=False),
        sa.Column('ml_confidence', sa.Float(), nullable=False),
        sa.Column('model_name', sa.String(60), nullable=False),
        sa.Column('simple_explanation', sa.Text(), nullable=False),
        sa.Column('technical_explanation', sa.JSON(), nullable=False),
        sa.Column('verification_status', sa.String(30), nullable=False),
        sa.Column('verification_summary', sa.Text(), nullable=False),
        sa.Column('sources', sa.JSON(), nullable=False),
        sa.Column('final_assessment', sa.String(30), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_predictions_user_id', 'predictions', ['user_id'])

def downgrade():
    op.drop_table('predictions')
    op.drop_table('password_reset_tokens')
    op.drop_table('users')
