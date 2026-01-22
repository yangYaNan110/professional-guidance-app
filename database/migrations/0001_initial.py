"""初始数据库迁移"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 创建用户表
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('nickname', sa.String(100)),
        sa.Column('avatar_url', sa.String(500)),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_active', sa.Boolean, default=True),
    )

    # 创建用户画像表
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id')),
        sa.Column('education', sa.String(100)),
        sa.Column('major', sa.String(200)),
        sa.Column('skills', sa.JSON),
        sa.Column('experience_years', sa.Integer),
        sa.Column('expected_salary_min', sa.Integer),
        sa.Column('expected_salary_max', sa.Integer),
        sa.Column('preferred_locations', sa.JSON),
        sa.Column('preferred_industries', sa.JSON),
        sa.Column('career_goals', sa.Text),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )

    # 创建对话历史表
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id')),
        sa.Column('title', sa.String(200)),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )

    # 创建对话消息表
    op.create_table(
        'messages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('conversation_id', sa.String(36), sa.ForeignKey('conversations.id')),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('audio_url', sa.String(500)),
        sa.Column('emotion', sa.String(50)),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )

    # 创建岗位表
    op.create_table(
        'jobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('company', sa.String(200), nullable=False),
        sa.Column('company_id', sa.String(36)),
        sa.Column('location', sa.String(200)),
        sa.Column('salary_min', sa.Integer),
        sa.Column('salary_max', sa.Integer),
        sa.Column('salary_avg', sa.Integer),
        sa.Column('description', sa.Text),
        sa.Column('requirements', sa.JSON),
        sa.Column('skills', sa.JSON),
        sa.Column('industry', sa.String(100)),
        sa.Column('job_type', sa.String(50)),
        sa.Column('experience_required', sa.String(50)),
        sa.Column('education_required', sa.String(50)),
        sa.Column('source', sa.String(50)),
        sa.Column('source_url', sa.String(500)),
        sa.Column('crawled_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )

    # 创建推荐记录表
    op.create_table(
        'recommendations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id')),
        sa.Column('job_id', sa.String(36), sa.ForeignKey('jobs.id')),
        sa.Column('score', sa.Float),
        sa.Column('reason', sa.Text),
        sa.Column('is_viewed', sa.Boolean, default=False),
        sa.Column('is_saved', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )

    # 创建索引
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_jobs_industry', 'jobs', ['industry'])
    op.create_index('idx_jobs_source', 'jobs', ['source'])
    op.create_index('idx_recommendations_user', 'recommendations', ['user_id'])

def downgrade() -> None:
    op.drop_index('idx_recommendations_user', table_name='recommendations')
    op.drop_index('idx_jobs_source', table_name='jobs')
    op.drop_index('idx_jobs_industry', table_name='jobs')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('recommendations')
    op.drop_table('jobs')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('user_profiles')
    op.drop_table('users')
